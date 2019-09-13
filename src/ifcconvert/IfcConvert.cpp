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
#include "../ifcgeom/IfcGeomRenderStyles.h"

#include "../ifcparse/utils.h"

#include <IGESControl_Controller.hxx>
#include <Standard_Version.hxx>

#include <boost/program_options.hpp>
#include <boost/make_shared.hpp>

#include <fstream>
#include <sstream>
#include <set>
#include <time.h>

#if USE_VLD
#include <vld.h>
#endif

#ifdef _MSC_VER
#include <io.h>
#include <fcntl.h>
#endif
// C++11 header:
#include <random>

#if defined(_MSC_VER) && defined(_UNICODE)
typedef std::wstring path_t;
static std::wostream& cout_ = std::wcout;
static std::wostream& cerr_ = std::wcerr;
#else
typedef std::string path_t;
static std::ostream& cout_ = std::cout;
static std::ostream& cerr_ = std::cerr;
#endif

const std::string DEFAULT_EXTENSION = ".obj";
const std::string TEMP_FILE_EXTENSION = ".tmp";

namespace po = boost::program_options;

void print_version()
{
    cout_ << "IfcOpenShell " << IfcSchema::Identifier << " IfcConvert " << IFCOPENSHELL_VERSION << " (OCC " << OCC_VERSION_STRING_EXT << ")\n";
}

void print_usage(bool suggest_help = true)
{
    cout_ << "Usage: IfcConvert [options] <input.ifc> [<output>]\n"
        << "\n"
        << "Converts the geometry in an IFC file into one of the following formats:\n"
        << "  .obj   WaveFront OBJ  (a .mtl file is also created)\n"
#ifdef WITH_OPENCOLLADA
        << "  .dae   Collada        Digital Assets Exchange\n"
#endif
        << "  .stp   STEP           Standard for the Exchange of Product Data\n"
        << "  .igs   IGES           Initial Graphics Exchange Specification\n"
        << "  .xml   XML            Property definitions and decomposition tree\n"
        << "  .svg   SVG            Scalable Vector Graphics (2D floor plan)\n"
        << "\n"
        << "If no output filename given, <input>" << IfcUtil::path::from_utf8(DEFAULT_EXTENSION) << " will be used as the output file.\n";
    if (suggest_help) {
        cout_ << "\nRun 'IfcConvert --help' for more information.";
    }
    cout_ << std::endl;
}

/// @todo Add help for single option
void print_options(const po::options_description& options)
{
#if defined(_MSC_VER) && defined(_UNICODE)
	// See issue https://svn.boost.org/trac10/ticket/10952
	std::ostringstream temp;
	temp << options;
	cout_ << "\n" << temp.str().c_str();
#else
	cout_ << "\n" << options;
#endif
	cout_ << std::endl;
}

template <typename T>
T change_extension(const T& fn, const T& ext) {
	typename T::size_type dot = fn.find_last_of('.');
	if (dot != T::npos) {
		return fn.substr(0, dot) + ext;
	} else {
		return fn + ext;
	}
}

bool file_exists(const std::string& filename) {
    std::ifstream file(IfcUtil::path::from_utf8(filename).c_str());
    return file.good();
}

static std::basic_stringstream<path_t::value_type> log_stream;
void write_log(bool);
std::string format_duration(time_t start, time_t end);

/// @todo make the filters non-global
IfcGeom::entity_filter entity_filter; // Entity filter is used always by default.
IfcGeom::layer_filter layer_filter;
const std::string NAME_ARG = "Name", GUID_ARG = "GlobalId", DESC_ARG = "Description", TAG_ARG = "Tag";
boost::array<std::string, 4> supported_args = { { NAME_ARG, GUID_ARG, DESC_ARG, TAG_ARG } };
IfcGeom::string_arg_filter guid_filter(IfcSchema::Type::IfcRoot, 0); // IfcRoot.GlobalId
// Note: skipping IfcRoot OwnerHistory, argument index 1
IfcGeom::string_arg_filter name_filter(IfcSchema::Type::IfcRoot, 2); // IfcRoot.Name
IfcGeom::string_arg_filter desc_filter(IfcSchema::Type::IfcRoot, 3); // IfcRoot.Description
IfcGeom::string_arg_filter tag_filter(IfcSchema::Type::IfcProxy, 8, IfcSchema::Type::IfcElement, 7); // IfcProxy.Tag & IfcElement.Tag

struct geom_filter
{
    geom_filter(bool include, bool traverse) : type(UNUSED), include(include), traverse(traverse) {}
    geom_filter() : type(UNUSED), include(false), traverse(false) {}
    enum filter_type { UNUSED, ENTITY_TYPE, LAYER_NAME, ENTITY_ARG };
    filter_type type;
    bool include;
    bool traverse;
    std::string arg;
    std::set<std::string> values;
};
// Specialized classes for knowing which type of filter we are validating within validate().
// Could not figure out easily how else to know it if using single type for both.
struct inclusion_filter : public geom_filter { inclusion_filter() : geom_filter(true, false) {} };
struct inclusion_traverse_filter : public geom_filter { inclusion_traverse_filter() : geom_filter(true, true) {} };
struct exclusion_filter : public geom_filter { exclusion_filter() : geom_filter(false, false) {} };
struct exclusion_traverse_filter : public geom_filter { exclusion_traverse_filter() : geom_filter(false, true) {} };

size_t read_filters_from_file(const std::string&, inclusion_filter&, inclusion_traverse_filter&, exclusion_filter&, exclusion_traverse_filter&);
void parse_filter(geom_filter &, const std::vector<std::string>&);
std::vector<IfcGeom::filter_t> setup_filters(const std::vector<geom_filter>&, const std::string&);

bool init_input_file(const std::string& filename, IfcParse::IfcFile& ifc_file, bool no_progress, bool mmap);

#if defined(_MSC_VER) && defined(_UNICODE)
int wmain(int argc, wchar_t** argv) {
	typedef po::wcommand_line_parser command_line_parser;
	typedef wchar_t char_t;

	_setmode(_fileno(stdout), _O_U16TEXT);
	_setmode(_fileno(stderr), _O_U16TEXT);
#else
int main(int argc, char** argv) {
	typedef po::command_line_parser command_line_parser;
	typedef char char_t;
#endif

	double deflection_tolerance;
	inclusion_filter include_filter;
	inclusion_traverse_filter include_traverse_filter;
	exclusion_filter exclude_filter;
	exclusion_traverse_filter exclude_traverse_filter;
	path_t filter_filename;
	path_t default_material_filename;
	std::string log_format;

    po::options_description generic_options("Command line options");
	generic_options.add_options()
		("help,h", "display usage information")
		("version", "display version information")
		("verbose,v", "more verbose log messages")
		("quiet,q", "less status and progress output")
		("stderr-progress", "output progress to stderr stream")
		("yes,y", "answer 'yes' automatically to possible confirmation queries (e.g. overwriting an existing output file)")
		("no-progress", "suppress possible progress bar type of prints that use carriage return")
		("log-format", po::value<std::string>(&log_format), "log format: plain or json");

    po::options_description fileio_options;
	fileio_options.add_options()
#ifdef USE_MMAP
		("mmap", "use memory-mapped file for input")
#endif
		("input-file", new po::typed_value<path_t, char_t>(0), "input IFC file")
		("output-file", new po::typed_value<path_t, char_t>(0), "output geometry file");

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
            "Specifies that the entities that match a specific filtering criteria are to be included in the geometrical output:\n"
            "1) 'entities': the following list of types should be included. SVG output defaults "
            "to IfcSpace to be included. The entity names are handled case-insensitively.\n"
            "2) 'layers': the entities that are assigned to presentation layers of which names "
            "match the given values should be included.\n"
            "3) 'arg <ArgumentName>': the following list of values for that specific argument should be included. "
            "Currently supported arguments are GlobalId, Name, Description, and Tag.\n\n"
            "The values for 'layers' and 'arg' are handled case-sensitively (wildcards supported)."
            "--include and --exclude cannot be placed right before input file argument and "
            "only single of each argument supported for now. See also --exclude.")
        ("include+", po::value<inclusion_traverse_filter>(&include_traverse_filter)->multitoken(),
            "Same as --include but applies filtering also to the decomposition and/or containment (IsDecomposedBy, "
            "HasOpenings, FillsVoid, ContainedInStructure) of the filtered entity, e.g. --include+=arg Name \"Level 1\" "
            "includes entity with name \"Level 1\" and all of its children. See --include for more information. ")
        ("exclude", po::value<exclusion_filter>(&exclude_filter)->multitoken(),
            "Specifies that the entities that match a specific filtering criteria are to be excluded in the geometrical output."
            "See --include for syntax and more details. The default value is '--exclude=entities IfcOpeningElement IfcSpace'.")
        ("exclude+", po::value<exclusion_traverse_filter>(&exclude_traverse_filter)->multitoken(),
            "Same as --exclude but applies filtering also to the decomposition and/or containment "
            "of the filtered entity. See --include+ for more details.")
        ("no-normals",
            "Disables computation of normals. Saves time and file size and is useful "
            "in instances where you're going to recompute normals for the exported "
            "model in other modelling application in any case.")
        ("deflection-tolerance", po::value<double>(&deflection_tolerance)->default_value(1e-3),
            "Sets the deflection tolerance of the mesher, 1e-3 by default if not specified.")
        ("generate-uvs",
            "Generates UVs (texture coordinates) by using simple box projection. Requires normals. "
            "Not guaranteed to work properly if used with --weld-vertices.")
        ("filter-file", new po::typed_value<path_t, char_t>(&filter_filename),
            "Specifies a filter file that describes the used filtering criteria. Supported formats "
            "are '--include=arg GlobalId ...' and 'include arg GlobalId ...'. Spaces and tabs can be used as delimiters."
            "Multiple filters of same type with different values can be inserted on their own lines. "
            "See --include, --include+, --exclude, and --exclude+ for more details.")
        ("default-material-file", new po::typed_value<path_t, char_t>(&default_material_filename),
            "Specifies a material file that describes the material object types will have"
            "if an object does not have any specified material in the IFC file.");


    std::string bounds, offset_str, rotation_str;
#ifdef HAVE_ICU
    std::string unicode_mode;
#endif
    short precision;
	double section_height;
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
		("section-height", po::value<double>(&section_height),
		    "Specifies the cut section height for SVG 2D geometry.")
        ("use-element-names",
            "Use entity names instead of unique IDs for naming elements upon serialization. "
            "Applicable for OBJ, DAE, and SVG output.")
        ("use-element-guids",
            "Use entity GUIDs instead of unique IDs for naming elements upon serialization. "
            "Applicable for OBJ, DAE, and SVG output.")
        ("use-material-names",
            "Use material names instead of unique IDs for naming materials upon serialization. "
            "Applicable for OBJ and DAE output.")
		("use-element-types",
			"Use element types instead of unique IDs for naming elements upon serialization. "
			"Applicable for DAE output.")
		("use-element-hierarchy",
			"Order the elements using their IfcBuildingStorey parent. "
			"Applicable for DAE output.")
        ("center-model",
            "Centers the elements upon serialization by applying the center point of "
            "all placements as an offset. Applicable for OBJ and DAE output. Can take several minutes on large models.")
        ("model-offset", po::value<std::string>(&offset_str),
            "Applies an arbitrary offset of form 'x;y;z' to all placements.")
        ("model-rotation", po::value<std::string>(&rotation_str),
             "Applies an arbitrary quaternion rotation of form 'x;y;z;w' to all placements.")
		("site-local-placement",
			"Place elements locally in the IfcSite coordinate system, instead of placing "
			"them in the IFC global coords. Applicable for OBJ and DAE output.")
		("building-local-placement",
			"Similar to --site-local-placement, but placing elements in locally in the parent IfcBuilding coord system")
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
        po::store(command_line_parser(argc, argv).
            options(cmdline_options).positional(positional_options).run(), vmap);
    } catch (const po::unknown_option& e) {
        cerr_ << "[Error] Unknown option '" << e.get_option_name().c_str() << "'\n\n";
        print_usage();
        return EXIT_FAILURE;
    } catch (const po::error_with_option_name& e) {
        cerr_ << "[Error] Invalid usage of '" << e.get_option_name().c_str() << "': " << e.what() << "\n\n";
        return EXIT_FAILURE;
    } catch (const std::exception& e) {
        cerr_ << "[Error] " << e.what() << "\n\n";
        print_usage();
        return EXIT_FAILURE;
    } catch (...) {
		cerr_ << "[Error] Unknown error parsing command line options\n\n";
        print_usage();
        return EXIT_FAILURE;
    }

    po::notify(vmap);

	const bool mmap = vmap.count("mmap") != 0;
	const bool verbose = vmap.count("verbose") != 0;
	const bool no_progress = vmap.count("no-progress") != 0;
	const bool quiet = vmap.count("quiet") != 0;
	const bool stderr_progress = vmap.count("stderr-progress") != 0;
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
	const bool use_element_guids = vmap.count("use-element-guids") != 0;
	const bool use_material_names = vmap.count("use-material-names") != 0;
	const bool use_element_types = vmap.count("use-element-types") != 0;
	const bool use_element_hierarchy = vmap.count("use-element-hierarchy") != 0;
	const bool no_normals = vmap.count("no-normals") != 0;
	const bool center_model = vmap.count("center-model") != 0;
	const bool model_offset = vmap.count("model-offset") != 0;
	const bool model_rotation = vmap.count("model-rotation") != 0;
	const bool site_local_placement = vmap.count("site-local-placement") != 0;
	const bool building_local_placement = vmap.count("building-local-placement") != 0;
	const bool generate_uvs = vmap.count("generate-uvs") != 0;

    if (!quiet || vmap.count("version")) {
		print_version();
	}

	if (vmap.count("version")) {
        return EXIT_SUCCESS;
    } else if (vmap.count("help")) {
        print_usage(false);
        print_options(generic_options.add(geom_options).add(serializer_options));
        return EXIT_SUCCESS;
    } else if (!vmap.count("input-file")) {
        std::cerr << "[Error] Input file not specified" << std::endl;
        print_usage();
        return EXIT_FAILURE;
    }
    
	if (vmap.count("log-format") == 1) {
		boost::to_lower(log_format);
		if (log_format == "plain") {
			Logger::OutputFormat(Logger::FMT_PLAIN);
		} else if (log_format == "json") {
			Logger::OutputFormat(Logger::FMT_JSON);
		} else {
			std::cerr << "[Error] --log-format should be either plain or json" << std::endl;
			print_usage();
			return EXIT_FAILURE;
		}
	}
    
    if (!filter_filename.empty()) {
        size_t num_filters = read_filters_from_file(IfcUtil::path::to_utf8(filter_filename), include_filter, include_traverse_filter, exclude_filter, exclude_traverse_filter);
        if (num_filters) {
            Logger::Notice(boost::lexical_cast<std::string>(num_filters) + " filters read from specifified file.");
        } else {
            std::cerr << "[Error] No filters read from specifified file.\n";
            return EXIT_FAILURE;
        }
    }

#ifdef HAVE_ICU
    if (!unicode_mode.empty()) {
        if (unicode_mode == "utf8") {
            IfcParse::IfcCharacterDecoder::mode = IfcParse::IfcCharacterDecoder::UTF8;
        } else if (unicode_mode == "escape") {
            IfcParse::IfcCharacterDecoder::mode = IfcParse::IfcCharacterDecoder::JSON;
        } else {
            cerr_ << "[Error] Invalid value for --unicode" << std::endl;
            print_options(serializer_options);
            return 1;
        }
    }
#endif

    if (!default_material_filename.empty()) {
        try {
            IfcGeom::set_default_style_file(IfcUtil::path::to_utf8(default_material_filename));
        } catch (const std::exception& e) {
            std::cerr << "[Error] Could not read default material file:" << std::endl;
            std::cerr << e.what() << std::endl;
            return EXIT_FAILURE;
        }
    }

	boost::optional<double> bounding_width;
	boost::optional<double> bounding_height;
	if (vmap.count("bounds") == 1) {
		int w, h;
		if (sscanf(bounds.c_str(), "%ux%u", &w, &h) == 2 && w > 0 && h > 0) {
			bounding_width = w;
			bounding_height = h;
		} else {
			cerr_ << "[Error] Invalid use of --bounds" << std::endl;
            print_options(serializer_options);
			return EXIT_FAILURE;
		}
	}

	const path_t input_filename = vmap["input-file"].as<path_t>();
    if (!file_exists(IfcUtil::path::to_utf8(input_filename))) {
        cerr_ << "[Error] Input file '" << input_filename << "' does not exist" << std::endl;
        return EXIT_FAILURE;
    }

	// If no output filename is specified a Wavefront OBJ file will be output
	// to maintain backwards compatibility with the obsolete IfcObj executable.
	const path_t output_filename = vmap.count("output-file") == 1 
		? vmap["output-file"].as<path_t>()
		: change_extension(input_filename, IfcUtil::path::from_utf8(DEFAULT_EXTENSION));
	
	if (output_filename.size() < 5) {
        cerr_ << "[Error] Invalid or unsupported output file '" << output_filename << "' given" << std::endl;
        print_usage();
		return EXIT_FAILURE;
	}

    if (file_exists(IfcUtil::path::to_utf8(output_filename)) && !vmap.count("yes")) {
        std::string answer;
        cout_ << "A file '" << output_filename << "' already exists. Overwrite the existing file?" << std::endl;
        std::cin >> answer;
        if (!boost::iequals(answer, "yes") && !boost::iequals(answer, "y")) {
            return EXIT_SUCCESS;
        }
    }

	Logger::SetOutput(&cout_, &log_stream);
	Logger::Verbosity(verbose ? Logger::LOG_NOTICE : Logger::LOG_ERROR);

    path_t output_temp_filename = output_filename + IfcUtil::path::from_utf8(TEMP_FILE_EXTENSION);

	path_t output_extension = output_filename.substr(output_filename.size()-4);
	boost::to_lower(output_extension);

    IfcParse::IfcFile ifc_file;

	const path_t OBJ = IfcUtil::path::from_utf8(".obj"),
		MTL = IfcUtil::path::from_utf8(".mtl"),
		DAE = IfcUtil::path::from_utf8(".dae"),
		STP = IfcUtil::path::from_utf8(".stp"),
		IGS = IfcUtil::path::from_utf8(".igs"),
		SVG = IfcUtil::path::from_utf8(".svg"),
		XML = IfcUtil::path::from_utf8(".xml");

    if (output_extension == XML) {
        int exit_code = EXIT_FAILURE;
        try {
            if (init_input_file(IfcUtil::path::to_utf8(input_filename), ifc_file, no_progress || quiet, mmap)) {
                time_t start, end;
                time(&start);
                XmlSerializer s(IfcUtil::path::to_utf8(output_temp_filename));
                s.setFile(&ifc_file);
                Logger::Status("Writing XML output...");
                s.finalize();
                time(&end);
                Logger::Status("Done! Conversion took " +  format_duration(start, end));

                IfcUtil::path::rename_file(IfcUtil::path::to_utf8(output_temp_filename), IfcUtil::path::to_utf8(output_filename));
                exit_code = EXIT_SUCCESS;
            }
        } catch (const std::exception& e) {
			Logger::Error(e);
		}
        write_log(!quiet);
        return exit_code;
    }

    /// @todo Clean up this filter code further.
    std::vector<geom_filter> used_filters;
    if (include_filter.type != geom_filter::UNUSED) { used_filters.push_back(include_filter); }
    if (include_traverse_filter.type != geom_filter::UNUSED) { used_filters.push_back(include_traverse_filter); }
    if (exclude_filter.type != geom_filter::UNUSED) { used_filters.push_back(exclude_filter); }
    if (exclude_traverse_filter.type != geom_filter::UNUSED) { used_filters.push_back(exclude_traverse_filter); }

    std::vector<IfcGeom::filter_t> filter_funcs = setup_filters(used_filters, IfcUtil::path::to_utf8(output_extension));
    if (filter_funcs.empty()) {
        cerr_ << "[Error] Failed to set up geometry filters\n";
        return EXIT_FAILURE;
    }

    if (!entity_filter.values.empty()) { entity_filter.update_description(); Logger::Notice(entity_filter.description); }
    if (!layer_filter.values.empty()) { layer_filter.update_description(); Logger::Notice(layer_filter.description); }
    if (!guid_filter.values.empty()) { guid_filter.update_description(); Logger::Notice(guid_filter.description); }
    if (!name_filter.values.empty()) { name_filter.update_description(); Logger::Notice(name_filter.description); }
    if (!desc_filter.values.empty()) { desc_filter.update_description(); Logger::Notice(desc_filter.description); }
    if (!tag_filter.values.empty()) { tag_filter.update_description(); Logger::Notice(tag_filter.description); }

#ifdef _MSC_VER
	if (output_extension == DAE || output_extension == STP || output_extension == IGS) {
#else
	if (output_extension == DAE) {
#endif
		// These serializers do not support opening unicode paths. Therefore
		// a random temp file is generated using only ASCII characters instead.
		std::random_device rng;
		std::uniform_int_distribution<int> index_dist('A', 'Z');
		{
			std::string v = ".ifcopenshell.";
			output_temp_filename += path_t(v.begin(), v.end());
		}
		for (int i = 0; i < 8; ++i) {
			output_temp_filename.push_back(static_cast<path_t::value_type>(index_dist(rng)));
		}
		{
			std::string v = ".tmp.";
			output_temp_filename += path_t(v.begin(), v.end());
		}
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
	settings.set(IfcGeom::IteratorSettings::SEARCH_FLOOR, use_element_hierarchy);
	settings.set(IfcGeom::IteratorSettings::SITE_LOCAL_PLACEMENT, site_local_placement);
	settings.set(IfcGeom::IteratorSettings::BUILDING_LOCAL_PLACEMENT, building_local_placement);


    settings.set(SerializerSettings::USE_ELEMENT_NAMES, use_element_names);
    settings.set(SerializerSettings::USE_ELEMENT_GUIDS, use_element_guids);
    settings.set(SerializerSettings::USE_MATERIAL_NAMES, use_material_names);
	settings.set(SerializerSettings::USE_ELEMENT_TYPES, use_element_types);
	settings.set(SerializerSettings::USE_ELEMENT_HIERARCHY, use_element_hierarchy);
    settings.set_deflection_tolerance(deflection_tolerance);
    settings.precision = precision;

    if (model_offset && center_model) {
        Logger::Error("Cannot use --center-model together with --model-offset");
        return EXIT_FAILURE;
    }

    if (model_offset) {
        std::array<double,3> &offset = settings.offset;
        if (sscanf(offset_str.c_str(), "%lf;%lf;%lf", &offset[0], &offset[1], &offset[2]) != 3) {
            cerr_ << "[Error] Invalid use of --model-offset\n" << offset_str;
            IfcUtil::path::delete_file(IfcUtil::path::to_utf8(output_temp_filename));
            print_options(serializer_options);
            return EXIT_FAILURE;
        }

        std::stringstream msg;
        msg << "Using model offset (" << offset[0] << "," << offset[1] << "," << offset[2] << ")";
        Logger::Notice(msg.str());
    }

    if (model_rotation) {
        std::array<double,4> &rotation = settings.rotation;
        if (sscanf(rotation_str.c_str(), "%lf;%lf;%lf;%lf", &rotation[0], &rotation[1], &rotation[2], &rotation[3]) != 4) {
            cerr_ << "[Error] Invalid use of --model-rotation\n" << rotation_str;
            IfcUtil::path::delete_file(IfcUtil::path::to_utf8(output_temp_filename));
            print_options(serializer_options);
            return EXIT_FAILURE;
        }

        std::stringstream msg;
        msg << "Using model rotation (" << rotation[0] << "," << rotation[1] << "," << rotation[2] << "," << rotation[3] << ")";
        Logger::Notice(msg.str());
    }

	boost::shared_ptr<GeometrySerializer> serializer; /**< @todo use std::unique_ptr when possible */
	if (output_extension == OBJ) {
        // Do not use temp file for MTL as it's such a small file.
        const path_t mtl_filename = change_extension(output_filename, MTL);
		if (!use_world_coords) {
			Logger::Notice("Using world coords when writing WaveFront OBJ files");
			settings.set(IfcGeom::IteratorSettings::USE_WORLD_COORDS, true);
		}
		serializer = boost::make_shared<WaveFrontOBJSerializer>(IfcUtil::path::to_utf8(output_temp_filename), IfcUtil::path::to_utf8(mtl_filename), settings);
#ifdef WITH_OPENCOLLADA
	} else if (output_extension == DAE) {
		serializer = boost::make_shared<ColladaSerializer>(IfcUtil::path::to_utf8(output_temp_filename), settings);
#endif
	} else if (output_extension == STP) {
		serializer = boost::make_shared<StepSerializer>(IfcUtil::path::to_utf8(output_temp_filename), settings);
	} else if (output_extension == IGS) {
		IGESControl_Controller::Init(); // work around Open Cascade bug
		serializer = boost::make_shared<IgesSerializer>(IfcUtil::path::to_utf8(output_temp_filename), settings);
	} else if (output_extension == SVG) {
		settings.set(IfcGeom::IteratorSettings::DISABLE_TRIANGULATION, true);
		serializer = boost::make_shared<SvgSerializer>(IfcUtil::path::to_utf8(output_temp_filename), settings);
		if (vmap.count("section-height") != 0) {
			Logger::Notice("Overriding section height");
			static_cast<SvgSerializer*>(serializer.get())->setSectionHeight(section_height);
		}
		if (bounding_width.is_initialized() && bounding_height.is_initialized()) {
            static_cast<SvgSerializer*>(serializer.get())->setBoundingRectangle(bounding_width.get(), bounding_height.get());
		}
	} else {
        cerr_ << "[Error] Unknown output filename extension '" << output_extension << "'\n";
		write_log(!quiet);
		print_usage();
		return EXIT_FAILURE;
	}

    if (use_element_hierarchy && output_extension != DAE) {
        cerr_ << "[Error] --use-element-hierarchy can be used only with .dae output.\n";
        /// @todo Lots of duplicate error-and-exit code.
		write_log(!quiet);
		print_usage();
		IfcUtil::path::delete_file(IfcUtil::path::to_utf8(output_temp_filename));
		return EXIT_FAILURE;
	}

    const bool is_tesselated = serializer->isTesselated(); // isTesselated() doesn't change at run-time
	if (!is_tesselated) {
		if (weld_vertices) {
            Logger::Notice("Weld vertices setting ignored when writing non-tesselated output");
		}
        if (generate_uvs) {
            Logger::Notice("Generate UVs setting ignored when writing non-tesselated output");
        }
        if (center_model || model_offset) {
            Logger::Notice("Centering/offsetting model setting ignored when writing non-tesselated output");
        }

        settings.set(IfcGeom::IteratorSettings::DISABLE_TRIANGULATION, true);
	}

	if (!serializer->ready()) {
		IfcUtil::path::delete_file(IfcUtil::path::to_utf8(output_temp_filename));
		write_log(!quiet);
		return EXIT_FAILURE;
	}

	time_t start,end;
	time(&start);
	
    if (!init_input_file(IfcUtil::path::to_utf8(input_filename), ifc_file, no_progress || quiet, mmap)) {
        write_log(!quiet);
		serializer.reset();
        IfcUtil::path::delete_file(IfcUtil::path::to_utf8(output_temp_filename)); /**< @todo Windows Unicode support */
        return EXIT_FAILURE;
    }

    IfcGeom::Iterator<real_t> context_iterator(settings, &ifc_file, filter_funcs);
    if (!context_iterator.initialize()) {
        /// @todo It would be nice to know and print separate error prints for a case where we found no entities
        /// and for a case we found no entities that satisfy our filtering criteria.
        Logger::Error("No geometrical entities found");
		serializer.reset();
		IfcUtil::path::delete_file(IfcUtil::path::to_utf8(output_temp_filename));
        write_log(!quiet);
        return EXIT_FAILURE;
    }

    serializer->setFile(context_iterator.getFile());

	if (convert_back_units) {
		serializer->setUnitNameAndMagnitude(context_iterator.getUnitName(), static_cast<float>(context_iterator.getUnitMagnitude()));
	} else {
		serializer->setUnitNameAndMagnitude("METER", 1.0f);
	}

	serializer->writeHeader();

	int old_progress = quiet ? 0 : -1;

    if (is_tesselated && center_model) {
        double* offset = serializer->settings().serializer_offset;

        if (site_local_placement || building_local_placement) {
            Logger::Error("Cannot use --center-model together with --{site,building}-local-placement");
            return EXIT_FAILURE;
        }

        if (!quiet) Logger::Status("Computing bounds...");
        context_iterator.compute_bounds();
        if (!quiet) Logger::Status("Done!");

        gp_XYZ center = (context_iterator.bounds_min() + context_iterator.bounds_max()) * 0.5;
        offset[0] = -center.X();
        offset[1] = -center.Y();
        offset[2] = -center.Z();

        std::stringstream msg;
        msg << "Using model offset (" << offset[0] << "," << offset[1] << "," << offset[2] << ")";
        Logger::Notice(msg.str());
    }

	if (!quiet) {
		Logger::Status("Creating geometry...");
	}

	// The functions IfcGeom::Iterator::get() and IfcGeom::Iterator::next() 
	// wrap an iterator of all geometrical products in the Ifc file. 
	// IfcGeom::Iterator::get() returns an IfcGeom::TriangulationElement or 
	// -BRepElement pointer, based on current settings. (see IfcGeomIterator.h 
	// for definition) IfcGeom::Iterator::next() is used to poll whether more 
	// geometrical entities are available. None of these functions throw 
	// exceptions, neither for parsing errors or geometrical errors. Upon 
	// calling next() the entity to be returned has already been processed, a 
	// non-null return value guarantees that a successfully processed product is 
	// available. 
	size_t num_created = 0;
	
	do {
        IfcGeom::Element<real_t> *geom_object = context_iterator.get();

		if (is_tesselated)
		{
			serializer->write(static_cast<const IfcGeom::TriangulationElement<real_t>*>(geom_object));
		}
		else
		{
			serializer->write(static_cast<const IfcGeom::BRepElement<real_t>*>(geom_object));
		}

        if (!no_progress) {
			if (quiet) {
				const int progress = context_iterator.progress();
				for (; old_progress < progress; ++old_progress) {
					std::cout << ".";
					if (stderr_progress)
						std::cerr << ".";
				}
				std::cout << std::flush;
				if (stderr_progress)
					std::cerr << std::flush;
			} else {
				const int progress = context_iterator.progress() / 2;
				if (old_progress != progress) Logger::ProgressBar(progress);
				old_progress = progress;
			}
        }
    } while (++num_created, context_iterator.next());

	if (!no_progress && quiet) {
		for (; old_progress < 100; ++old_progress) {
			std::cout << ".";
			if (stderr_progress)
				std::cerr << ".";
		}
		std::cout << std::flush;
		if (stderr_progress)
			std::cerr << std::flush;
	} else {
		Logger::Status("\rDone creating geometry (" + boost::lexical_cast<std::string>(num_created) +
			" objects)                                ");
	}

    serializer->finalize();
    // Make sure the dtor is explicitly run here (e.g. output files are closed before renaming them).
    serializer.reset();

    // Renaming might fail (e.g. maybe the existing file was open in a viewer application)
    // Do not remove the temp file as user can salvage the conversion result from it.
    bool successful = IfcUtil::path::rename_file(IfcUtil::path::to_utf8(output_temp_filename), IfcUtil::path::to_utf8(output_filename));
    if (!successful) {
        cerr_ << "Unable to write output file '" << output_filename << "', see '" <<
            output_temp_filename << "' for the conversion result.";
    }

	write_log(!quiet);

	time(&end);

    if (!quiet) {
        Logger::Status("\nConversion took " +  format_duration(start, end));
    }

    return successful ? EXIT_SUCCESS : EXIT_FAILURE;
}

std::string format_duration(time_t start, time_t end)
{
    int seconds = (int)difftime(end, start);
    std::stringstream ss;
    int minutes = seconds / 60;
    seconds = seconds % 60;
    if (minutes > 0) {
        ss << minutes << " minute";
        if (minutes == 0 || minutes > 1) {
            ss << "s";
        }
        ss << " ";
    }
    ss << seconds << " second";
    if (seconds == 0 || seconds > 1) {
        ss << "s";
    }
    return ss.str();
}

void write_log(bool header) {
	path_t log = log_stream.str();
	if (!log.empty()) {
        if (header) {
            cout_ << "\nLog:\n";
        }
        cout_ << log << std::endl;
	}
}

bool init_input_file(const std::string &filename, IfcParse::IfcFile &ifc_file, bool no_progress, bool mmap)
{
    time_t start, end;

    // Prevent IfcFile::Init() prints by setting output to null temporarily
    if (no_progress) { Logger::SetOutput(NULL, &log_stream); }

    time(&start);
#ifdef USE_MMAP
	if (!ifc_file.Init(filename, mmap)) {
#else
	(void)mmap;
	if (!ifc_file.Init(filename)) {
#endif
        Logger::Error("Unable to parse input file '" + filename + "'");
        return false;
    }
    time(&end);

    if (no_progress) { Logger::SetOutput(&cout_, &log_stream); }
    else {  Logger::Status("Parsing input file took " + format_duration(start, end)); }

    return true;
}

bool append_filter(const std::string& type, const std::vector<std::string>& values, geom_filter& filter)
{
    geom_filter temp;
    parse_filter(temp, values);
    // Merge values only if type and arg match.
    if ((filter.type != geom_filter::UNUSED && filter.type != temp.type) || (!filter.arg.empty() && filter.arg != temp.arg)) {
        cerr_ << "[Error] Multiple '" << type.c_str() << "' filters specified with different criteria\n";
        return false;
    }
    filter.type = temp.type;
    filter.values.insert(temp.values.begin(), temp.values.end());
    filter.arg = temp.arg;
    return true;
}

size_t read_filters_from_file(
    const std::string& filename,
    inclusion_filter& include_filter,
    inclusion_traverse_filter& include_traverse_filter,
    exclusion_filter& exclude_filter,
    exclusion_traverse_filter& exclude_traverse_filter)
{
    std::ifstream filter_file(IfcUtil::path::from_utf8(filename).c_str());

    if (!filter_file.is_open()) {
        cerr_ << "[Error] Unable to open filter file '" << IfcUtil::path::from_utf8(filename) << "' or the file does not exist.\n";
        return 0;
    }

    size_t line_number = 1, num_filters = 0;
    for (std::string line; std::getline(filter_file, line); ++line_number) {
        boost::trim(line);
        if (line.empty()) {
            continue;
        }

        std::vector<std::string> values;
        boost::split(values, line, boost::is_any_of("\t "), boost::token_compress_on);
        if (values.empty()) {
            continue;
        }

        std::string type = values.front();
        values.erase(values.begin());
        // Support both "--include=arg GlobalId 1VQ5n5$RrEbPk8le4ZCI81" and "include arg GlobalId 1VQ5n5$RrEbPk8le4ZCI81"
        // and tolerate extraneous whitespace.
        boost::trim_left_if(type, boost::is_any_of("-"));
        size_t equal_pos = type.find('=');
        if (equal_pos != std::string::npos) {
            std::string value = type.substr(equal_pos + 1);
            type = type.substr(0, equal_pos);
            values.insert(values.begin(), value);
        }

        try {
            if (type == "include") { if (append_filter("include", values, include_filter)) { ++num_filters; } }
            else if (type == "include+") { if (append_filter("include+", values, include_traverse_filter)) { ++num_filters; } }
            else if (type == "exclude") { if (append_filter("exclude", values, exclude_filter)) { ++num_filters; } }
            else if (type == "exclude+") { if (append_filter("exclude+", values, exclude_traverse_filter)) { ++num_filters; } }
            else {
                cerr_ << "[Error] Invalid filtering type at line " << boost::lexical_cast<path_t>(line_number) << "\n";
                return 0;
            }
        } catch(...) {
            cerr_ << "[Error] Unable to parse filter at line " << boost::lexical_cast<path_t>(line_number) << ".\n";
            return 0;
        }
    }
    return num_filters;
}

void parse_filter(geom_filter &filter, const std::vector<std::string>& values)
{
    if (values.size() == 0) {
        throw po::validation_error(po::validation_error::at_least_one_value_required);
    }
    std::string type = *values.begin();
    if (type == "entities") {
        filter.type = geom_filter::ENTITY_TYPE;
    } else if (type == "layers") {
        filter.type = geom_filter::LAYER_NAME;
    } else if (type == "arg") {
        filter.type = geom_filter::ENTITY_ARG;
        filter.arg = *(values.begin() + 1);
        if (std::find(supported_args.begin(), supported_args.end(), filter.arg) == supported_args.end()) {
            throw po::validation_error(po::validation_error::invalid_option_value);
        }
    } else {
        throw po::validation_error(po::validation_error::invalid_option_value);
    }
    filter.values.insert(values.begin() + (filter.type == geom_filter::ENTITY_ARG ? 2 : 1), values.end());
}

void validate(boost::any& v, const std::vector<std::string>& values, inclusion_filter*, int)
{
    /// @todo For now only single --include, --include+, --exclude, or --exclude+ supported. Support having multiple.
    po::validators::check_first_occurrence(v);
    inclusion_filter filter;
    parse_filter(filter, values);
    v = filter;
}

void validate(boost::any& v, const std::vector<std::string>& values, inclusion_traverse_filter*, int)
{
    po::validators::check_first_occurrence(v);
    inclusion_traverse_filter filter;
    parse_filter(filter, values);
    v = filter;
}

void validate(boost::any& v, const std::vector<std::string>& values, exclusion_filter*, int)
{
    po::validators::check_first_occurrence(v);
    exclusion_filter filter;
    parse_filter(filter, values);
    v = filter;
}

void validate(boost::any& v, const std::vector<std::string>& values, exclusion_traverse_filter*, int)
{
    po::validators::check_first_occurrence(v);
    exclusion_traverse_filter filter;
    parse_filter(filter, values);
    v = filter;
}


/// @todo Clean up this filter initialization code further.
/// @return References to the used filter functors, if none an error occurred.
std::vector<IfcGeom::filter_t> setup_filters(const std::vector<geom_filter>& filters, const std::string& output_extension)
{
    std::vector<IfcGeom::filter_t> filter_funcs;
    BOOST_FOREACH(const geom_filter& f, filters) {
        if (f.type == geom_filter::ENTITY_TYPE) {
            entity_filter.include = f.include;
            entity_filter.traverse = f.traverse;
            try {
                entity_filter.populate(f.values);
            } catch (const IfcParse::IfcException& e) {
                cerr_ << "[Error] " << e.what() << std::endl;
                return std::vector<IfcGeom::filter_t>();
            }
        } else if (f.type == geom_filter::LAYER_NAME) {
            layer_filter.include = f.include;
            layer_filter.traverse = f.traverse;
            layer_filter.populate(f.values);
        } else if (f.type == geom_filter::ENTITY_ARG) {
            if (f.arg == GUID_ARG) {
                guid_filter.include = f.include;
                guid_filter.traverse = f.traverse;
                guid_filter.populate(f.values);
            } else if (f.arg == NAME_ARG) {
                name_filter.include = f.include;
                name_filter.traverse = f.traverse;
                name_filter.populate(f.values);
            } else if (f.arg == DESC_ARG) {
                desc_filter.include = f.include;
                desc_filter.traverse = f.traverse;
                desc_filter.populate(f.values);
            } else if (f.arg == TAG_ARG) {
                tag_filter.include = f.include;
                tag_filter.traverse = f.traverse;
                tag_filter.populate(f.values);
            }
        }
    }

    // If no entity names are specified these are the defaults to skip from output
    if (entity_filter.values.empty()) {
        try {
            std::set<std::string> entities;
            entities.insert("IfcSpace");
            if (output_extension == ".svg") {
                entity_filter.include = true;
            } else {
                entities.insert("IfcOpeningElement");
            }
            entity_filter.populate(entities);
        } catch (const IfcParse::IfcException& e) {
            cerr_ << "[Error] " << e.what() << std::endl;
            return std::vector<IfcGeom::filter_t>();
        }
    }

    if (!layer_filter.values.empty()) { filter_funcs.push_back(boost::ref(layer_filter));  }
    if (!entity_filter.values.empty()) { filter_funcs.push_back(boost::ref(entity_filter)); }
    if (!guid_filter.values.empty()) { filter_funcs.push_back(boost::ref(guid_filter)); }
    if (!name_filter.values.empty()) { filter_funcs.push_back(boost::ref(name_filter)); }
    if (!desc_filter.values.empty()) { filter_funcs.push_back(boost::ref(desc_filter)); }
    if (!tag_filter.values.empty()) { filter_funcs.push_back(boost::ref(tag_filter)); }

    return filter_funcs;
}
