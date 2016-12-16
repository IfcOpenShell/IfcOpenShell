/********************************************************************************
 *                                                                              *
 * This file is part of IfcOpenShell.                                           *
 *                                                                              *
 * IfcOpenShell is free software: you can redistribute it and/or modify         *
 * it under the terms of the Lesser GNU General Public License as published by  *
 * the Free Software Foundation, either version 3.0 of the License, or          *
 * (at your option) any later version.                                          *
 *                                                                              *
 * IfcOpenShell is distributed in the hope that it will be useful,              *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of               *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 *
 * Lesser GNU General Public License for more details.                          *
 *                                                                              *
 * You should have received a copy of the Lesser GNU General Public License     *
 * along with this program. If not, see <http://www.gnu.org/licenses/>.         *
 *                                                                              *
 ********************************************************************************/

/********************************************************************************
 *                                                                              *
 * This started as a brief example of how IfcOpenShell can be interfaced from   * 
 * within a C++ context, it has since then evolved into a fullfledged command   *
 * line application that is able to convert geometry in an IFC files into       *
 * several tesselated and topological output formats.                           *
 *                                                                              *
 ********************************************************************************/

#include "../ifcconvert/ColladaSerializer.h"
#include "../ifcconvert/IgesSerializer.h"
#include "../ifcconvert/StepSerializer.h"
#include "../ifcconvert/WavefrontObjSerializer.h"
#include "../ifcconvert/XmlSerializer.h"
#include "../ifcconvert/SvgSerializer.h"

#include "../ifcgeom/IfcGeomIterator.h"

#include <IGESControl_Controller.hxx>
#include <Standard_Version.hxx>

#include <boost/program_options.hpp>
#include <boost/algorithm/string.hpp>

#include <fstream>
#include <sstream>
#include <set>
#include <time.h>

#if USE_VLD
#include <vld.h>
#endif

const std::string DEFAULT_EXTENSION = "obj";
const std::string TEMP_FILE_EXTENSION = ".tmp";

namespace po = boost::program_options;

void print_version()
{
    /// @todo Why cerr used for info prints? Change to cout.
    std::cerr << "IfcOpenShell " << IfcSchema::Identifier << " IfcConvert " << IFCOPENSHELL_VERSION << std::endl;
}

void print_usage(bool suggest_help = true)
{
    std::cerr << "Usage: IfcConvert [options] <input.ifc> [<output>]" << "\n"
        << "\n"
        << "Converts the geometry in an IFC file into one of the following formats:" << "\n"
        << "  .obj   WaveFront OBJ  (a .mtl file is also created)" << "\n"
#ifdef WITH_OPENCOLLADA
        << "  .dae   Collada        Digital Assets Exchange" << "\n"
#endif
        << "  .stp   STEP           Standard for the Exchange of Product Data" << "\n"
        << "  .igs   IGES           Initial Graphics Exchange Specification" << "\n"
        << "  .xml   XML            Property definitions and decomposition tree" << "\n"
        << "  .svg   SVG            Scalable Vector Graphics (2D floor plan)" << "\n"
        << "\n"
        << "If no output filename given, <input>." + DEFAULT_EXTENSION + " will be used as the output file.\n";
    if (suggest_help) {
        std::cerr << "\nRun 'IfcConvert --help' for more information.";
    }
    std::cerr << std::endl;
}

void print_options(const po::options_description& options)
{
    std::cerr << "\n" << options;
    std::cerr << std::endl;
}

std::string change_extension(const std::string& fn, const std::string& ext) {
	std::string::size_type dot = fn.find_last_of('.');
	if (dot != std::string::npos) {
		return fn.substr(0,dot+1) + ext;
	} else {
		return fn + "." + ext;
	}
}

bool file_exists(const std::string& filename)
{
    /// @todo Windows Unicode support
    std::ifstream file(filename.c_str());
    return file.good();
}

bool rename_file(const std::string& old_filename, const std::string& new_filename)
{
    // Whether or not rename() replaces an existing file is implementation-specific,
    // so remove() possible existing file always.
    /// @todo Windows Unicode support
    std::remove(new_filename.c_str());
    return std::rename(old_filename.c_str(), new_filename.c_str()) == 0;
}

static std::stringstream log_stream;
void write_log();

/// @todo Make this a feature of IfcGeom::Iterator instead.
/// Also add GUID filtering.
struct geom_filter
{
    bool include;
    enum filter_type { ENTITIES, NAMES };
    filter_type type;
    std::set<std::string> values;
};
// Specialized classes for knowing which type of filter we are validating within validate().
// Could not figure out easily how else to know it if using single type for both.
struct inclusion_filter : public geom_filter { inclusion_filter() { include = true; } };
struct exclusion_filter : public geom_filter { exclusion_filter() { include = false; } };

int main(int argc, char** argv)
{
    po::options_description generic_options("Command line options");
	generic_options.add_options()
		("help,h", "display usage information")
		("version", "display version information")
        ("verbose,v", "more verbose output")
        ("yes,y", "answer 'yes' automatically to possible confirmation queries (e.g. overwriting an existing output file)");

    po::options_description fileio_options;
	fileio_options.add_options()
		("input-file", po::value<std::string>(), "input IFC file")
		("output-file", po::value<std::string>(), "output geometry file");

    double deflection_tolerance;
    inclusion_filter include_filter;
    exclusion_filter exclude_filter;

    po::options_description geom_options("Geometry options");
	geom_options.add_options()
		("plan",
			"Specifies whether to include curves in the output result. Typically "
			"these are representations of type Plan or Axis. Excluded by default.")
		("model",
			"Specifies whether to include surfaces and solids in the output result. "
			"Typically these are representations of type Body or Facetation. "
			"Included by default.")
		("weld-vertices",
			"Specifies whether vertices are welded, meaning that the coordinates "
			"vector will only contain unique xyz-triplets. This results in a "
			"manifold mesh which is useful for modelling applications, but might "
			"result in unwanted shading artefacts in rendering applications.")
		("use-world-coords", 
			"Specifies whether to apply the local placements of building elements "
			"directly to the coordinates of the representation mesh rather than "
			"to represent the local placement in the 4x3 matrix, which will in that "
			"case be the identity matrix.")
		("convert-back-units",
			"Specifies whether to convert back geometrical output back to the "
			"unit of measure in which it is defined in the IFC file. Default is "
			"to use meters.")
		("sew-shells", 
			"Specifies whether to sew the faces of IfcConnectedFaceSets together. "
			"This is a potentially time consuming operation, but guarantees a "
			"consistent orientation of surface normals, even if the faces are not "
			"properly oriented in the IFC file.")
#if OCC_VERSION_HEX < 0x60900
		// In Open CASCADE version prior to 6.9.0 boolean operations with multiple
		// arguments where not introduced yet and a work-around was implemented to
		// subtract multiple openings as a single compound. This hack is obsolete
		// for newer versions of Open CASCADE.
		("merge-boolean-operands", 
			"Specifies whether to merge all IfcOpeningElement operands into a single "
			"operand before applying the subtraction operation. This may "
			"introduce a performance improvement at the risk of failing, in "
			"which case the subtraction is applied one-by-one.")
#endif
		("disable-opening-subtractions", 
			"Specifies whether to disable the boolean subtraction of "
			"IfcOpeningElement Representations from their RelatingElements.")
		("enable-layerset-slicing", 
			"Specifies whether to enable the slicing of products according "
			"to their associated IfcMaterialLayerSet.")
        ("include", po::value<inclusion_filter>(&include_filter)->multitoken(),
            "Specifies that the entities or names provided are to be included. "
            "If --include=entities specified, the following list of types should be included in the geometrical output. "
            "SVG output defaults to IfcSpace to be included. The entity names are handled case-insensitively. "
            "If --include=names specified, the following list of names or wildcard patterns should be included in the "
            "geometrical output. The name patterns are handled case-sensitively. Cannot be placed right before input file argument. "
            "Only single option supported for now.")
        ("exclude", po::value<exclusion_filter>(&exclude_filter)->multitoken(),
            "Specifies that the 'entities' or 'names' provided are to be excluded. Defaults to IfcOpeningElement and IfcSpace "
            "to be excluded. See --include for syntax and more details.")
        ("no-normals",
            "Disables computation of normals. Saves time and file size and is useful "
            "in instances where you're going to recompute normals for the exported "
            "model in other modelling application in any case.")
        ("deflection-tolerance", po::value<double>(&deflection_tolerance)->default_value(1e-3),
            "Sets the deflection tolerance of the mesher, 1e-3 by default if not specified.")
        ("generate-uvs",
            "Generates UVs (texture coordinates) by using simple box projection. Requires normals. "
            "Not guaranteed to work properly if used with --weld-vertices.")
        ("traverse",
            "Applies --include or --exclude also to the decomposition and/or containment (IsDecomposedBy, "
            "HasOpenings, FillsVoid, ContainedInStructure) of the filtered entity, e.g. --include=names \"Level 1\" "
            "--traverse includes entity with name \"Level 1\" and all of its children.");

    std::string bounds, offset_str;
#ifdef HAVE_ICU
    std::string unicode_mode;
#endif
    short precision;

    po::options_description serializer_options("Serialization options");
    serializer_options.add_options()
#ifdef HAVE_ICU
        ("unicode", po::value<std::string>(&unicode_mode),
            "Specifies the Unicode handling behavior when parsing the IFC file. "
            "Accepted values 'utf8' (the default) and 'escape'.")
#endif
        ("bounds", po::value<std::string>(&bounds),
            "Specifies the bounding rectangle, for example 512x512, to which the "
            "output will be scaled. Only used when converting to SVG.")
        ("use-element-names",
            "Use entity names instead of unique IDs for naming elements upon serialization. "
            "Applicable for OBJ, DAE, and SVG output.")
        ("use-element-guids",
            "Use entity GUIDs instead of unique IDs for naming elements upon serialization. "
            "Applicable for OBJ, DAE, and SVG output.")
        ("use-material-names",
            "Use material names instead of unique IDs for naming materials upon serialization. "
            "Applicable for OBJ and DAE output.")
        ("center-model",
            "Centers the elements upon serialization by applying the center point of "
            "all placements as an offset. Applicable for OBJ and DAE output.")
        ("model-offset", PO::value<std::string>(&offset_str),
            "Applies an arbitrary offset of form 'x;y;z' to all placements. Applicable for OBJ and DAE output.")
        ("precision", po::value<short>(&precision)->default_value(SerializerSettings::DEFAULT_PRECISION),
            "Sets the precision to be used to format floating-point values, 15 by default. "
            "Use a negative value to use the system's default precision (should be 6 typically). "
            "Applicable for OBJ and DAE output. For DAE output, value >= 15 means that up to 16 decimals are used, "
            " and any other value means that 6 or 7 decimals are used.");

    po::options_description cmdline_options;
	cmdline_options.add(generic_options).add(fileio_options).add(geom_options).add(serializer_options);

    po::positional_options_description positional_options;
	positional_options.add("input-file", 1);
	positional_options.add("output-file", 1);

    po::variables_map vmap;
    try {
        po::store(po::command_line_parser(argc, argv).
            options(cmdline_options).positional(positional_options).run(), vmap);
    } catch (const po::unknown_option& e) {
        std::cerr << "[Error] Unknown option '" << e.get_option_name() << "'" << "\n\n";
        print_usage();
        return EXIT_FAILURE;
    } catch (const po::error_with_option_name& e) {
        std::cerr << "[Error] Invalid usage of '" << e.get_option_name() << "': " << e.what() << "\n\n";
        print_usage();
        return EXIT_FAILURE;
    } catch (const std::exception& e) {
        std::cerr << "[Error] " << e.what() << "\n\n";
        print_usage();
        return EXIT_FAILURE;
    } catch (...) { // other errors such as invalid command line syntax
        print_usage();
        return 1;

    po::notify(vmap);

    print_version();

    if (vmap.count("version")) {
        return 0;
    } else if (vmap.count("help")) {
        print_usage(false);
        print_options(generic_options.add(geom_options).add(serializer_options));
        return 0;
    } else if (!vmap.count("input-file")) {
        std::cerr << "[Error] Input file not specified" << std::endl;
        print_usage();
        return 1;
    }
	const bool verbose = vmap.count("verbose") != 0;
	const bool weld_vertices = vmap.count("weld-vertices") != 0;
	const bool use_world_coords = vmap.count("use-world-coords") != 0;
	const bool convert_back_units = vmap.count("convert-back-units") != 0;
	const bool sew_shells = vmap.count("sew-shells") != 0;
#if OCC_VERSION_HEX < 0x60900
	const bool merge_boolean_operands = vmap.count("merge-boolean-operands") != 0;
#endif
	const bool disable_opening_subtractions = vmap.count("disable-opening-subtractions") != 0;
	const bool include_plan = vmap.count("plan") != 0;
	const bool include_model = vmap.count("model") != 0 || (!include_plan);
	const bool enable_layerset_slicing = vmap.count("enable-layerset-slicing") != 0;
    const bool use_element_names = vmap.count("use-element-names") != 0;
    const bool use_element_guids = vmap.count("use-element-guids") != 0 ;
    const bool use_material_names = vmap.count("use-material-names") != 0;
    const bool no_normals = vmap.count("no-normals") != 0 ;
    const bool center_model = vmap.count("center-model") != 0 ;
    const bool model_offset = vmap.count("model-offset") != 0 ;
    const bool generate_uvs = vmap.count("generate-uvs") != 0 ;
    const bool traverse = vmap.count("traverse") != 0;

#ifdef HAVE_ICU
    if (!unicode_mode.empty()) {
        if (unicode_mode == "utf8") {
            IfcParse::IfcCharacterDecoder::mode = IfcParse::IfcCharacterDecoder::UTF8;
        } else if (unicode_mode == "escape") {
            IfcParse::IfcCharacterDecoder::mode = IfcParse::IfcCharacterDecoder::JSON;
        } else {
            std::cerr << "[Error] Invalid value for --unicode" << std::endl;
            print_options(serializer_options);
            return 1;
        }
    }
#endif

	int bounding_width = -1, bounding_height = -1;
	if (vmap.count("bounds") == 1) {
		int w, h;
		if (sscanf(bounds.c_str(), "%ux%u", &w, &h) == 2 && w > 0 && h > 0) {
			bounding_width = w;
			bounding_height = h;
		} else {
			std::cerr << "[Error] Invalid use of --bounds" << std::endl;
            print_options(serializer_options);
			return 1;
		}
	}

	const std::string input_filename = vmap["input-file"].as<std::string>();
    if (!file_exists(input_filename)) {
        std::cerr << "[Error] Input file '" << input_filename << "' does not exist" << std::endl;
        return 1;
    }

	// If no output filename is specified a Wavefront OBJ file will be output
	// to maintain backwards compatibility with the obsolete IfcObj executable.
	const std::string output_filename = vmap.count("output-file") == 1 
		? vmap["output-file"].as<std::string>()
		: change_extension(input_filename, DEFAULT_EXTENSION);
	
	if (output_filename.size() < 5) {
        std::cerr << "[Error] Invalid or unsupported output file '" << output_filename << "' given" << std::endl;
        print_usage();
		return 1;
	}

    if (file_exists(output_filename) && !vmap.count("yes")) {
        std::string answer;
        std::cout << "A file '" << output_filename << "' already exists. Overwrite the existing file?" << std::endl;
        std::cin >> answer;
        if (!boost::iequals(answer, "yes") && !boost::iequals(answer, "y")) {
            return 0;
        }
    }

    std::string output_temp_filename = output_filename + TEMP_FILE_EXTENSION;

	std::string output_extension = output_filename.substr(output_filename.size()-4);
	boost::to_lower(output_extension);

	Logger::SetOutput(&std::cout, &log_stream);
	if (output_extension == ".xml") {
		int exit_code = 1;
		try {
			XmlSerializer s(output_temp_filename);
			IfcParse::IfcFile f;
			if (!f.Init(input_filename)) {
				Logger::Message(Logger::LOG_ERROR, "Unable to parse input file '" + input_filename + "'");
			} else {
				s.setFile(&f);
                Logger::Status("Writing XML output...");
				s.finalize();
                Logger::Status("Done!");
                rename_file(output_temp_filename, output_filename);
				exit_code = 0;
			}
		} catch (...) {}
		write_log();
		return exit_code;
	}

    SerializerSettings settings;
	/// @todo Make APPLY_DEFAULT_MATERIALS configurable? Quickly tested setting this to false and using obj exporter caused the program to crash and burn.
	settings.set(IfcGeom::IteratorSettings::APPLY_DEFAULT_MATERIALS,      true);
	settings.set(IfcGeom::IteratorSettings::USE_WORLD_COORDS,             use_world_coords);
	settings.set(IfcGeom::IteratorSettings::WELD_VERTICES,                weld_vertices);
	settings.set(IfcGeom::IteratorSettings::SEW_SHELLS,                   sew_shells);
	settings.set(IfcGeom::IteratorSettings::CONVERT_BACK_UNITS,           convert_back_units);
#if OCC_VERSION_HEX < 0x60900
	settings.set(IfcGeom::IteratorSettings::FASTER_BOOLEANS,              merge_boolean_operands);
#endif
	settings.set(IfcGeom::IteratorSettings::DISABLE_OPENING_SUBTRACTIONS, disable_opening_subtractions);
	settings.set(IfcGeom::IteratorSettings::INCLUDE_CURVES,               include_plan);
	settings.set(IfcGeom::IteratorSettings::EXCLUDE_SOLIDS_AND_SURFACES,  !include_model);
	settings.set(IfcGeom::IteratorSettings::APPLY_LAYERSETS,              enable_layerset_slicing);
    settings.set(IfcGeom::IteratorSettings::NO_NORMALS, no_normals);
    settings.set(IfcGeom::IteratorSettings::GENERATE_UVS, generate_uvs);
    settings.set(IfcGeom::IteratorSettings::TRAVERSE, traverse);

    settings.set(SerializerSettings::USE_ELEMENT_NAMES, use_element_names);
    settings.set(SerializerSettings::USE_ELEMENT_GUIDS, use_element_guids);
    settings.set(SerializerSettings::USE_MATERIAL_NAMES, use_material_names);
    settings.precision = precision;

	GeometrySerializer* serializer;
	if (output_extension == ".obj") {
        // Do not use temp file for MTL as it's such a small file.
        const std::string mtl_filename = change_extension(output_filename, "mtl");
		if (!use_world_coords) {
			Logger::Message(Logger::LOG_NOTICE, "Using world coords when writing WaveFront OBJ files");
			settings.set(IfcGeom::IteratorSettings::USE_WORLD_COORDS, true);
		}
		serializer = new WaveFrontOBJSerializer(output_temp_filename, mtl_filename, settings);
#ifdef WITH_OPENCOLLADA
	} else if (output_extension == ".dae") {
		serializer = new ColladaSerializer(output_temp_filename, settings);
#endif
	} else if (output_extension == ".stp") {
		serializer = new StepSerializer(output_temp_filename, settings);
	} else if (output_extension == ".igs") {
		IGESControl_Controller::Init(); // work around Open Cascade bug
		serializer = new IgesSerializer(output_temp_filename, settings);
	} else if (output_extension == ".svg") {
		settings.set(IfcGeom::IteratorSettings::DISABLE_TRIANGULATION, true);
		serializer = new SvgSerializer(output_temp_filename, settings);
		if (bounding_width && bounding_height) {
            static_cast<SvgSerializer*>(serializer)->setBoundingRectangle(bounding_width, bounding_height);
		}
	} else {
		Logger::Message(Logger::LOG_ERROR, "Unknown output filename extension '" + output_extension + "'");
		write_log();
		print_usage();
		return 1;
	}

    const bool is_tesselated = serializer->isTesselated(); // isTesselated() doesn't change at run-time
	if (!is_tesselated) {
		if (weld_vertices) {
            Logger::Message(Logger::LOG_NOTICE, "Weld vertices setting ignored when writing non-tesselated output");
		}
        if (generate_uvs) {
            Logger::Message(Logger::LOG_NOTICE, "Generate UVs setting ignored when writing non-tesselated output");
        }
        if (center_model || model_offset) {
            Logger::Message(Logger::LOG_NOTICE, "Centering/offsetting model setting ignored when writing non-tesselated output");
        }

        settings.set(IfcGeom::IteratorSettings::DISABLE_TRIANGULATION, true);
	}

    IfcGeom::Iterator<real_t> context_iterator(settings, input_filename);

	try {
		if (include_entities) {
			context_iterator.includeEntities(entities);
		} else {
			context_iterator.excludeEntities(entities);
		}
	} catch (const IfcParse::IfcException& e) {
		std::cout << "[Error] " << e.what() << std::endl;
		return 1;
	}

    if (include_names) {
        context_iterator.include_entity_names(names);
    } else {
        context_iterator.exclude_entity_names(names);
    }

	if (!serializer->ready()) {
		write_log();
		return 1;
	}

	time_t start,end;
	time(&start);
	
	if (!context_iterator.initialize()) {
        /// @todo It would be nice to know and print separate error prints for a case where we failed to parse
        /// the file and for a case where we found no entities that satisfy our filtering criteria.
        Logger::Message(Logger::LOG_ERROR, "Unable to parse input file '" + input_filename + "' or no geometrical entities found");
		write_log();
		return 1;
	}

    serializer->setFile(context_iterator.getFile());

	if (convert_back_units) {
		serializer->setUnitNameAndMagnitude(context_iterator.getUnitName(), static_cast<float>(context_iterator.getUnitMagnitude()));
	} else {
		serializer->setUnitNameAndMagnitude("METER", 1.0f);
	}

	serializer->writeHeader();

	int old_progress = -1;

    if (center_model || model_offset) {
        double* offset = serializer->settings().offset;
        if (center_model) {
            gp_XYZ center = (context_iterator.bounds_min() + context_iterator.bounds_max()) * 0.5;
            offset[0] = -center.X();
            offset[1] = -center.Y();
            offset[2] = -center.Z();
        } else {
            if (sscanf(offset_str.c_str(), "%lf;%lf;%lf", &offset[0], &offset[1], &offset[2]) != 3) {
                std::cerr << "[Error] Invalid use of --model-offset\n";
                print_options(serializer_options);
                return 1;
            }
        }

        std::stringstream msg;
        msg << "Using model offset (" << offset[0] << "," << offset[1] << "," << offset[2] << ")";
        Logger::Message(Logger::LOG_NOTICE, msg.str());
    }

	Logger::Status("Creating geometry...");

	// The functions IfcGeom::Iterator::get() and IfcGeom::Iterator::next() 
	// wrap an iterator of all geometrical products in the Ifc file. 
	// IfcGeom::Iterator::get() returns an IfcGeom::TriangulationElement or 
	// -BRepElement pointer, based on current settings. (see IfcGeomIterator.h 
	// for definition) IfcGeom::Iterator::next() is used to poll whether more 
	// geometrical entities are available. None of these functions throw 
	// exceptions, neither for parsing errors or geometrical errors. Upon 
	// calling next() the entity to be returned has already been processed, a 
	// true return value guarantees that a successfully processed product is 
	// available. 
	size_t num_created = 0;
	
	do {
        IfcGeom::Element<real_t> *geom_object = context_iterator.get();
		if (is_tesselated) {
			serializer->write(static_cast<const IfcGeom::TriangulationElement<real_t>*>(geom_object));
		} else {
			serializer->write(static_cast<const IfcGeom::BRepElement<real_t>*>(geom_object));
		}
        const int progress = context_iterator.progress() / 2;
        if (old_progress != progress) Logger::ProgressBar(progress);
        old_progress = progress;
    } while (++num_created, context_iterator.next());

    Logger::Status("\rDone creating geometry (" + boost::lexical_cast<std::string>(num_created) +
        " objects)                                ");

    serializer->finalize();
	delete serializer;

    // Renaming might fail (e.g. maybe the existing file was open in a viewer application)
    // Do not remove the temp file as user can salvage the conversion result from it.
    bool successful = rename_file(output_temp_filename, output_filename);
    if (!successful) {
        Logger::Message(Logger::LOG_ERROR, "Unable to write output file '" + output_filename + "'");
    }

	write_log();

	time(&end);

    int seconds = (int)difftime(end, start);
	std::stringstream msg;
	int minutes = seconds / 60;
	seconds = seconds % 60;
	msg << "\nConversion took";
	if (minutes > 0) {
		msg << " " << minutes << " minute";
		if (minutes > 1) {
			msg << "s";
		}
	}
	msg << " " << seconds << " second";
	if (seconds > 1) {
		msg << "s";
	}
	Logger::Status(msg.str());

    return successful ? 0 : 1;
}

void write_log() {
	std::string log = log_stream.str();
	if (!log.empty()) {
		std::cerr << "\n" << "Log:\n" << log << std::endl;
	}
}

/// @todo Duplicate code for inclusion_filter and exclusion_filter validation.
void validate(boost::any& v, const std::vector<std::string>& values, inclusion_filter*, int)
{
    /// @todo For now only single --include or --exclude supported. Support having multiple.
    po::validators::check_first_occurrence(v);
    inclusion_filter filter;

    if (values.size() == 0) {
        throw po::validation_error(po::validation_error::at_least_one_value_required);
    }
    std::string type = *values.begin();
    if (type == "entities") {
        filter.type = geom_filter::ENTITIES;
    } else if (type == "names") {
        filter.type = geom_filter::NAMES;
    } else {
        throw po::validation_error(po::validation_error::invalid_option_value);
    }
    filter.values.insert(values.begin() + 1, values.end());
    v = filter;
}

void validate(boost::any& v, const std::vector<std::string>& values, exclusion_filter*, int)
{
    po::validators::check_first_occurrence(v);
    exclusion_filter filter;

    if (values.size() == 0) {
        throw po::validation_error(po::validation_error::at_least_one_value_required);
    }
    std::string type = *values.begin();
    if (type == "entities") {
        filter.type = geom_filter::ENTITIES;
    } else if (type == "names") {
        filter.type = geom_filter::NAMES;
    } else {
        throw po::validation_error(po::validation_error::invalid_option_value);
    }
    filter.values.insert(values.begin() + 1, values.end());
    v = filter;
}
