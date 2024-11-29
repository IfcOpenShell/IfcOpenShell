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
 * several tessellated and topological output formats.                          *
 *                                                                              *
 ********************************************************************************/

// windows stuff: defines max as a macro when including windows.h
// error C2589: '(': illegal token on right side of '::'
#define NOMINMAX

#include "../serializers/ColladaSerializer.h"
#include "../serializers/GltfSerializer.h"
#include "../serializers/HdfSerializer.h"
#include "../serializers/IgesSerializer.h"
#include "../serializers/StepSerializer.h"
#include "../serializers/WavefrontObjSerializer.h"
#include "../serializers/XmlSerializer.h"
#include "../serializers/SvgSerializer.h"
#include "../serializers/USDSerializer.h"
#include "../serializers/TtlWktSerializer.h"

#include "../ifcgeom/IfcGeomFilter.h"
#include "../ifcgeom/Iterator.h"
#include "../ifcgeom/IfcGeomRenderStyles.h"

#include "../ifcparse/utils.h"

#ifdef IFOPSH_WITH_CITYJSON
#include "./cityjson/geobim.h"
#endif

#ifdef IFOPSH_WITH_OPENCASCADE

#include <Standard_Version.hxx>

#if OCC_VERSION_HEX < 0x60900
#include <IGESControl_Controller.hxx>
#endif

#endif

#include <boost/program_options.hpp>
#include <boost/make_shared.hpp>

#include <fstream>
#include <sstream>
#include <set>
#include <time.h>
#include <iomanip>

#if USE_VLD
#include <vld.h>
#endif

#ifdef _MSC_VER
#include <io.h>
#include <fcntl.h>
#endif

#include <random>
#include <thread>

#if defined(_MSC_VER) && defined(_UNICODE)
typedef std::wstring path_t;
typedef std::wofstream ofstream_t;
static std::wostream& cout_ = std::wcout;
static std::wostream& cerr_ = std::wcerr;
#else
typedef std::string path_t;
typedef std::ofstream ofstream_t;
static std::ostream& cout_ = std::cout;
static std::ostream& cerr_ = std::cerr;
#endif

const std::string DEFAULT_EXTENSION = ".obj";
const std::string TEMP_FILE_EXTENSION = ".tmp";

namespace po = boost::program_options;

void print_version()
{
    cout_ << "IfcOpenShell IfcConvert " << IFCOPENSHELL_VERSION;
#ifdef IFOPSH_WITH_OPENCASCADE
    cout_ << " (OCC " << OCC_VERSION_STRING_EXT << ")";
#endif
    cout_ << "\n";
}

void print_usage(bool suggest_help = true)
{
    cout_ << "Usage: IfcConvert [options] <input.ifc> [<output>]\n"
        << "\n"
        << "Converts (the geometry in) an IFC file into one of the following formats:\n"
        << "  .obj   WaveFront OBJ  (a .mtl file is also created)\n"
#ifdef WITH_OPENCOLLADA
        << "  .dae   Collada        Digital Assets Exchange\n"
#endif
#ifdef WITH_GLTF
		<< "  .glb   glTF           Binary glTF v2.0\n"
#endif
#ifdef WITH_USD
		<< "  .usd   USD            Universal Scene Description\n"
#endif
        << "  .stp   STEP           Standard for the Exchange of Product Data\n"
        << "  .igs   IGES           Initial Graphics Exchange Specification\n"
        << "  .xml   XML            Property definitions and decomposition tree\n"
        << "  .svg   SVG            Scalable Vector Graphics (2D floor plan)\n"
#ifdef WITH_HDF5
		<< "  .h5    HDF            Hierarchical Data Format storing positions, normals and indices\n"
#endif
#ifdef IFOPSH_WITH_CGAL
		<< "  .cityjson             City JSON format for geospatial data\n"
#endif
		<< "  .ttl   TTL/WKT        RDF Turtle with Well-Known-Text geometry\n"
		<< "  .ifc   IFC-SPF        Industry Foundation Classes\n"
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
void fix_quantities(IfcParse::IfcFile&, bool, bool, bool);
std::string format_duration(time_t start, time_t end);

/// @todo make the filters non-global
IfcGeom::entity_filter entity_filter; // Entity filter is used always by default.
IfcGeom::layer_filter layer_filter;
IfcGeom::attribute_filter attribute_filter;

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

bool init_input_file(const std::string& filename, IfcParse::IfcFile*& ifc_file, bool no_progress, bool mmap);

// from https://stackoverflow.com/questions/31696328/boost-program-options-using-zero-parameter-options-multiple-times
struct verbosity_counter {
	int count;
	verbosity_counter(int c = 0) {
		count = c;
	}
};

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

	inclusion_filter include_filter;
	inclusion_traverse_filter include_traverse_filter;
	exclusion_filter exclude_filter;
	exclusion_traverse_filter exclude_traverse_filter;
	path_t filter_filename;
	path_t default_material_filename;
	path_t log_file;
	path_t cache_file;
	std::string log_format;
	std::string geometry_kernel;

    po::options_description generic_options("Command line options");
	verbosity_counter vcounter;
	generic_options.add_options()
		("help,h", "display usage information")
		("version", "display version information")
		("verbose,v", po::value(&vcounter)->zero_tokens(), "more verbose log messages. Use twice (-vv) for debugging level.")
		("debug,d", "write boolean operands to file in current directory for debugging purposes")
		("quiet,q", "less status and progress output")
#ifdef WITH_HDF5
		("cache", "cache geometry creation. Use --cache-file to specify cache file path.")
#endif
		("stderr-progress", "output progress to stderr stream")
		("yes,y", "answer 'yes' automatically to possible confirmation queries (e.g. overwriting an existing output file)")
		("no-progress", "suppress possible progress bar type of prints that use carriage return")
		("log-format", po::value<std::string>(&log_format), "log format: plain or json")
		("log-file", new po::typed_value<path_t, char_t>(&log_file), "redirect log output to file");

    po::options_description fileio_options;
	fileio_options.add_options()
#ifdef USE_MMAP
		("mmap", "use memory-mapped file for input")
#endif
		("input-file", new po::typed_value<path_t, char_t>(0), "input IFC file")
		("output-file", new po::typed_value<path_t, char_t>(0), "output geometry file")
#ifdef WITH_HDF5
		("cache-file", new po::typed_value<path_t, char_t>(&cache_file), "geometry cache file")
#endif
		;

	po::options_description ifc_options("IFC options");
	ifc_options.add_options()
		("calculate-quantities", "Calculate or fix the physical quantity definitions "
			"based on an interpretation of the geometry when exporting IFC");

	int num_threads;
	std::string offset_str, rotation_str;

	std::string default_kernel;
#ifdef IFOPSH_WITH_CGAL
	default_kernel = "cgal";
#endif
#ifdef IFOPSH_WITH_OPENCASCADE
	default_kernel = "opencascade";
#endif

	// none, convex-decomposition, minkowski-triangles or halfspace-snapping
	std::string exterior_only_algo;

	ifcopenshell::geometry::Settings geometry_settings;
    
	po::options_description geom_options("Geometry options");
	geom_options.add_options()
		("kernel", po::value<std::string>(&geometry_kernel)->default_value(default_kernel),
			"Geometry kernel to use (opencascade, cgal, cgal-simple).")
		("threads,j", po::value<int>(&num_threads)->default_value(1),
			"Number of parallel processing threads for geometry interpretation.")
		("center-model",
            "Centers the elements by applying the center point of all placements as an offset."
            "Can take several minutes on large models.")
		("center-model-geometry",
            "Centers the elements by applying the center point of all mesh vertices as an offset.")
		("include", po::value<inclusion_filter>(&include_filter)->multitoken(),
			"Specifies that the instances that match a specific filtering criteria are to be included in the geometrical output:\n"
			"1) 'entities': the following list of types should be included. SVG output defaults "
			"to IfcSpace to be included. The entity names are handled case-insensitively.\n"
			"2) 'layers': the instances that are assigned to presentation layers of which names "
			"match the given values should be included.\n"
			"3) 'attribute <AttributeName>': products whose value for <AttributeName> should be included\n. "
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
		("filter-file", new po::typed_value<path_t, char_t>(&filter_filename),
			"Specifies a filter file that describes the used filtering criteria. Supported formats "
			"are '--include=arg GlobalId ...' and 'include arg GlobalId ...'. Spaces and tabs can be used as delimiters."
			"Multiple filters of same type with different values can be inserted on their own lines. "
			"See --include, --include+, --exclude, and --exclude+ for more details.")
        ("default-material-file", new po::typed_value<path_t, char_t>(&default_material_filename),
            "Specifies a material file that describes the material object types will have"
            "if an object does not have any specified material in the IFC file.")
		("exterior-only",
			po::value<std::string>(&exterior_only_algo)->default_value("none")->implicit_value("minkowski-triangles"),
			"Export only the exterior shell of the building found by geometric analysis. convex-decomposition, minkowski-triangles or halfspace-snapping")
		("plan", "Specifies whether to include curves in the output result. Typically "
			"these are representations of type Plan or Axis. Excluded by default.")
		("model", "Specifies whether to include surfaces and solids in the output result. "
			"Typically these are representations of type Body or Facetation. ")
		;
	
	geometry_settings.define_options(geom_options);

    std::string bounds;
#ifdef HAVE_ICU
    std::string unicode_mode;
#endif
    short precision;
	double section_height;
	std::string svg_scale, svg_center;
	std::string section_ref, elevation_ref, elevation_ref_guid;
	// "none", "full" or "left"
	std::string storey_height_display;
#ifdef IFOPSH_WITH_OPENCASCADE
	SvgSerializer::storey_height_display_types svg_storey_height_display = SvgSerializer::SH_NONE;
#endif

	ifcopenshell::geometry::SerializerSettings serializer_settings;

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
		("scale", po::value<std::string>(&svg_scale),
			"Interprets SVG bounds in mm, centers layout and draw elements to scale. "
			"Only used when converting to SVG. Example 1:100.")
		("center", po::value<std::string>(&svg_center),
			"When using --scale, specifies the location in the range [0 1]x[0 1] around which"
			"to center the drawings. Example 0.5x0.5 (default).")
		("section-ref", po::value<std::string>(&section_ref),
			"Element at which cross sections should be created")
		("elevation-ref", po::value<std::string>(&elevation_ref),
			"Element at which drawings should be created")
		("elevation-ref-guid", po::value<std::string>(&elevation_ref_guid),
			"Element guids at which drawings should be created")
		("auto-section",
			"Creates SVG cross section drawings automatically based on model extents")
		("auto-elevation",
			"Creates SVG elevation drawings automatically based on model extents")
		("draw-storey-heights",
			po::value<std::string>(&storey_height_display)->default_value("none")->implicit_value("full"),
			"Draws a horizontal line at the height of building storeys in vertical drawings")
		("storey-height-line-length", po::value<double>(), 
			"Length of the line when --draw-storey-heights=left")
		("svg-xmlns",
			"Stores name and guid in a separate namespace as opposed to data-name, data-guid")
		("svg-poly",
			"Uses the polygonal algorithm for hidden line rendering")
		("svg-prefilter",
			"Prefilter faces and shapes before feeding to HLR algorithm")
		("svg-segment-projection",
			"Segment result of projection wrt original products")
		("svg-write-poly",
			"Approximate every curve as polygonal in SVG output")
		("svg-project",
			"Always enable hidden line rendering instead of only on elevations")
		("svg-without-storeys", "Don't emit drawings for building storeys")
		("svg-no-css", "Don't emit CSS style declarations")
		("door-arcs", "Draw door openings arcs for IfcDoor elements")
		("section-height", po::value<double>(&section_height),
		    "Specifies the cut section height for SVG 2D geometry.")
		("section-height-from-storeys", "Derives section height from storey elevation. Use --section-height to override default offset of 1.2")
		("print-space-names", "Prints IfcSpace LongName and Name in the geometry output. Applicable for SVG output")
		("print-space-areas", "Prints calculated IfcSpace areas in square meters. Applicable for SVG output")
		("space-name-transform", po::value<std::string>(),
			"Additional transform to the space labels in SVG")
		;

	serializer_settings.define_options(serializer_options);

    po::options_description cmdline_options;
	cmdline_options.add(generic_options).add(fileio_options).add(geom_options).add(ifc_options).add(serializer_options);

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
	const bool no_progress = vmap.count("no-progress") != 0;
	const bool quiet = vmap.count("quiet") != 0;
	const bool stderr_progress = vmap.count("stderr-progress") != 0;

	const bool center_model = vmap.count("center-model") != 0;
	const bool center_model_geometry = vmap.count("center-model-geometry") != 0;

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
        cerr_ << "[Error] Input file not specified" << std::endl;
        print_usage();
        return EXIT_FAILURE;
    }

#ifdef IFOPSH_WITH_OPENCASCADE
	if (vmap.count("draw-storey-heights")) {
		boost::to_lower(storey_height_display);

		if (storey_height_display == "none") {
			svg_storey_height_display = SvgSerializer::SH_NONE;
		} else if (storey_height_display == "full") {
			svg_storey_height_display = SvgSerializer::SH_FULL;
		} else if (storey_height_display == "left") {
			svg_storey_height_display = SvgSerializer::SH_LEFT;
		} else {
			cerr_ << "[Error] --draw-storey-heights should be none|full|left" << std::endl;
			print_usage();
			return EXIT_FAILURE;
		}
	}
#endif

	if (num_threads <= 0) {
		num_threads = std::thread::hardware_concurrency();
		Logger::Notice("Using " + std::to_string(num_threads) + " threads");
	}
    
	if (vmap.count("log-format") == 1) {
		boost::to_lower(log_format);
		if (log_format == "plain") {
			Logger::OutputFormat(Logger::FMT_PLAIN);
		} else if (log_format == "json") {
			Logger::OutputFormat(Logger::FMT_JSON);
		} else {
			cerr_ << "[Error] --log-format should be either plain or json" << std::endl;
			print_usage();
			return EXIT_FAILURE;
		}
	}
    
    if (!filter_filename.empty()) {
        size_t num_filters = read_filters_from_file(IfcUtil::path::to_utf8(filter_filename), include_filter, include_traverse_filter, exclude_filter, exclude_traverse_filter);
        if (num_filters) {
            Logger::Notice(boost::lexical_cast<std::string>(num_filters) + " filters read from specifified file.");
        } else {
            cerr_ << "[Error] No filters read from specifified file.\n";
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
            cerr_ << "[Error] Could not read default material file:" << std::endl;
            cerr_ << e.what() << std::endl;
            return EXIT_FAILURE;
        }
    }

	boost::optional<double> bounding_width, bounding_height, relative_center_x, relative_center_y;

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

	if (vmap.count("center") == 1) {
		double cx, cy;
		if (sscanf(svg_center.c_str(), "%lfx%lf", &cx, &cy) == 2 && cx >= 0. && cy >= 0. && cx <= 1. && cy <= 1.) {
			relative_center_x = cx;
			relative_center_y = cy;
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

	ofstream_t log_fs;

	if (vmap.count("log-file")) {
		log_fs.open(log_file.c_str(), std::ios::app);
		Logger::SetOutput(quiet ? nullptr : &cout_, &log_fs);
	} else {
		Logger::SetOutput(quiet ? nullptr : &cout_, vcounter.count > 1 ? &cout_ : &log_stream);
	}

	switch (vcounter.count) {
	case 0:
		Logger::Verbosity(Logger::LOG_ERROR);
		break;
	case 1:
		Logger::Verbosity(Logger::LOG_NOTICE);
		break;
	case 2:
		Logger::Verbosity(Logger::LOG_DEBUG);
		break;
	case 3:
		Logger::Verbosity(Logger::LOG_PERF);
		break;
	case 4:
		Logger::Verbosity(Logger::LOG_PERF);
		Logger::PrintPerformanceStatsOnElement(true);
		break;
	}

    path_t output_temp_filename = output_filename + IfcUtil::path::from_utf8(TEMP_FILE_EXTENSION);
	
	std::vector<path_t> tokens;
	split(tokens, output_filename, boost::is_any_of("."));
	std::vector<path_t>::iterator tok_iter;
	path_t ext = *(tokens.end() - 1);
	path_t dot;
	dot = '.';	
	path_t output_extension = dot + ext;

	boost::to_lower(output_extension);

	IfcParse::IfcFile* ifc_file = 0;

	boost::optional<std::list<IfcGeom::Element*>> elems_from_adaptor;
    
    const path_t OBJ = IfcUtil::path::from_utf8(".obj"),
		MTL = IfcUtil::path::from_utf8(".mtl"),
		DAE = IfcUtil::path::from_utf8(".dae"),
		GLB = IfcUtil::path::from_utf8(".glb"),
		STP = IfcUtil::path::from_utf8(".stp"),
		IGS = IfcUtil::path::from_utf8(".igs"),
		SVG = IfcUtil::path::from_utf8(".svg"),
		CACHE = IfcUtil::path::from_utf8(".cache"),
		HDF = IfcUtil::path::from_utf8(".h5"),
		XML = IfcUtil::path::from_utf8(".xml"),
		CITY_JSON = IfcUtil::path::from_utf8(".cityjson"),
		IFC = IfcUtil::path::from_utf8(".ifc"),
		USD = IfcUtil::path::from_utf8(".usd"),
		USDA = IfcUtil::path::from_utf8(".usda"),
		USDC = IfcUtil::path::from_utf8(".usdc"),
		TTL = IfcUtil::path::from_utf8(".ttl");

	// @todo clean up serializer selection
	// @todo detect program options that conflict with the chosen serializer
	if (output_extension == XML) {
		int exit_code = EXIT_FAILURE;
		try {
			if (init_input_file(IfcUtil::path::to_utf8(input_filename), ifc_file, no_progress || quiet, mmap)) {
				time_t start, end;
				time(&start);
				XmlSerializer s(ifc_file, IfcUtil::path::to_utf8(output_temp_filename));
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
	} else if (output_extension == IFC) {
		int exit_code = EXIT_FAILURE;
		try {
			if (init_input_file(IfcUtil::path::to_utf8(input_filename), ifc_file, no_progress || quiet, mmap)) {
                time_t start, end;
				time(&start);
				std::ofstream fs(output_filename.c_str());
				if (fs.is_open()) {
					if (vmap.count("calculate-quantities")) {
						fix_quantities(*ifc_file, no_progress, quiet, stderr_progress);
					}
					fs << *ifc_file;
					exit_code = EXIT_SUCCESS;
				} else {
					Logger::Error("Unable to open output file for writing");
				}
                time(&end);
                Logger::Status("Done! Writing IFC took " +  format_duration(start, end));
			}
		} catch (const std::exception& e) {
			Logger::Error(e);
		}
		write_log(!quiet);
		return exit_code;
	}
#ifdef IFOPSH_WITH_CITYJSON
	else if (output_extension == CITY_JSON || (output_extension == OBJ || output_extension == DAE || output_extension == GLB) && vmap.count("exterior-only") && exterior_only_algo != "none") {

		// none, convex-decomposition, minkowski-triangles or halfspace-snapping
		boost::to_lower(exterior_only_algo);

		if (exterior_only_algo == "halfspace-snapping") {
			cerr_ << "[Error] halfspace-snapping not implemented yet" << std::endl;
			print_usage();
			return EXIT_FAILURE;
		} else if (exterior_only_algo == "minkowski-triangles") {
			// 
		} else if (exterior_only_algo == "convex-decomposition") {
			// 
		} else if (exterior_only_algo == "none") {
			// 
		} else {
			cerr_ << "[Error] --exterior-only should be convex-decomposition|minkowski-triangles|halfspace-snapping" << std::endl;
			print_usage();
			return EXIT_FAILURE;
		}

		geobim_settings settings;
		settings.input_filenames = { IfcUtil::path::to_utf8(input_filename) };
		settings.file = { new IfcParse::IfcFile(IfcUtil::path::to_utf8(input_filename)) };
		
		/*
		// No longer set, because we pass to real serializers now, awaiting a proper iterator adaptor
		if (output_extension == OBJ) {
			settings.obj_output_filename = IfcUtil::path::to_utf8(output_filename);
		}
		*/
	
		if (output_extension == CITY_JSON) {
			// we don't have a cityjson serializer though
			settings.cityjson_output_filename = IfcUtil::path::to_utf8(output_filename);
		}

		// @todo
		settings.radii = { "0.05" };
		settings.apply_openings = false;
		settings.apply_openings_posthoc = true;
		settings.debug = false;
		settings.exact_segmentation = true;
		settings.minkowski_triangles = exterior_only_algo == "minkowski-triangles";
		settings.no_erosion = false;
		settings.spherical_padding = false;
		if (num_threads != 1) {
			settings.threads = num_threads;
		}

		settings.settings.get<ifcopenshell::geometry::settings::UseWorldCoords>().value = false;
		settings.settings.get<ifcopenshell::geometry::settings::WeldVertices>().value = false;
		settings.settings.get<ifcopenshell::geometry::settings::ReorientShells>().value = true;
		settings.settings.get<ifcopenshell::geometry::settings::ConvertBackUnits>().value = true;
		settings.settings.get<ifcopenshell::geometry::settings::IteratorOutput>().value = ifcopenshell::geometry::settings::NATIVE;
		settings.settings.get<ifcopenshell::geometry::settings::DisableOpeningSubtractions>().value = !settings.apply_openings;

		if (include_filter.type != geom_filter::UNUSED) {
			settings.entity_names = include_filter.values;
			settings.entity_names_included = true;
		} else if (exclude_filter.type != geom_filter::UNUSED) {
			settings.entity_names = exclude_filter.values;
			settings.entity_names_included = false;
		} else {
			settings.entity_names = { { "IfcSpace", "IfcOpeningElement" } };
			settings.entity_names_included = false;
		}
		
		elems_from_adaptor.emplace();
		perform(settings, *elems_from_adaptor);
		
		if (output_extension == CITY_JSON) {
			return 0;
		}
		// else ... continue on to serialize elems_from_adaptor
	}
#endif

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

    if (!entity_filter.entity_names.empty()) { entity_filter.update_description(); Logger::Notice(entity_filter.description); }
    if (!layer_filter.values.empty()) { layer_filter.update_description(); Logger::Notice(layer_filter.description); }
	if (!attribute_filter.attribute_name.empty()) { attribute_filter.update_description(); Logger::Notice(attribute_filter.description); }

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
			output_temp_filename = path_t(v.begin(), v.end());
		}
		for (int i = 0; i < 8; ++i) {
			output_temp_filename.push_back(static_cast<path_t::value_type>(index_dist(rng)));
		}
		{
			std::string v = ".tmp";
			output_temp_filename += path_t(v.begin(), v.end());
		}
	}

	if (vmap[ifcopenshell::geometry::settings::WeldVertices::name].defaulted()) {
		geometry_settings.get<ifcopenshell::geometry::settings::WeldVertices>().value = false;
	}

	if (geometry_settings.get<ifcopenshell::geometry::settings::ForceSpaceTransparency>().has()) {
		IfcGeom::update_default_style("IfcSpace")->transparency = geometry_settings.get<ifcopenshell::geometry::settings::ForceSpaceTransparency>().get();
	}

	if (output_extension == OBJ || output_extension == STP || output_extension == IGS) {
		geometry_settings.get<ifcopenshell::geometry::settings::UseWorldCoords>().value = true;
	}

	if (output_extension == TTL) {
		geometry_settings.get<ifcopenshell::geometry::settings::TriangulationType>().value = ifcopenshell::geometry::settings::TriangulationMethod::POLYHEDRON_WITH_HOLES;
	}

	boost::shared_ptr<GeometrySerializer> serializer; /**< @todo use std::unique_ptr when possible */
	if (output_extension == OBJ) {
        // Do not use temp file for MTL as it's such a small file.
        const path_t mtl_filename = change_extension(output_filename, MTL);
		serializer = boost::make_shared<WaveFrontOBJSerializer>(IfcUtil::path::to_utf8(output_temp_filename), IfcUtil::path::to_utf8(mtl_filename), geometry_settings, serializer_settings);
#ifdef WITH_OPENCOLLADA
	} else if (output_extension == DAE) {
		serializer = boost::make_shared<ColladaSerializer>(IfcUtil::path::to_utf8(output_temp_filename), geometry_settings, serializer_settings);
#endif
#ifdef WITH_GLTF
	} else if (output_extension == GLB) {
		serializer = boost::make_shared<GltfSerializer>(IfcUtil::path::to_utf8(output_temp_filename), geometry_settings, serializer_settings);
#endif
#ifdef WITH_USD
	} else if (output_extension == USD || output_extension == USDA || output_extension == USDC) {
		serializer = boost::make_shared<USDSerializer>(IfcUtil::path::to_utf8(output_filename), geometry_settings, serializer_settings);
#endif
#ifdef IFOPSH_WITH_OPENCASCADE
	} else if (output_extension == STP) {
		serializer = boost::make_shared<StepSerializer>(IfcUtil::path::to_utf8(output_temp_filename), geometry_settings, serializer_settings);
	} else if (output_extension == IGS) {
#if OCC_VERSION_HEX < 0x60900
		// According to https://tracker.dev.opencascade.org/view.php?id=25689 something has been fixed in 6.9.0
		IGESControl_Controller::Init(); // work around Open Cascade bug
#endif
		serializer = boost::make_shared<IgesSerializer>(IfcUtil::path::to_utf8(output_temp_filename), geometry_settings, serializer_settings);
	} else if (output_extension == SVG) {
		geometry_settings.get<ifcopenshell::geometry::settings::IteratorOutput>().value = ifcopenshell::geometry::settings::NATIVE;
		serializer = boost::make_shared<SvgSerializer>(IfcUtil::path::to_utf8(output_temp_filename), geometry_settings, serializer_settings);
#ifdef WITH_HDF5
	} else if (output_extension == HDF) {
		geometry_settings.get<ifcopenshell::geometry::settings::IteratorOutput>().value = ifcopenshell::geometry::settings::NATIVE;
		serializer = boost::make_shared<HdfSerializer>(IfcUtil::path::to_utf8(output_temp_filename), geometry_settings, serializer_settings);
#endif
#endif	
	} else if (output_extension == TTL) {
		serializer = boost::make_shared<TtlWktSerializer>(IfcUtil::path::to_utf8(output_temp_filename), geometry_settings, serializer_settings);
	} else {
        cerr_ << "[Error] Unknown output filename extension '" << output_extension << "'\n";
		write_log(!quiet);
		print_usage();
		return EXIT_FAILURE;
	}

    if (geometry_settings.get<ifcopenshell::geometry::settings::UseElementHierarchy>().get() && output_extension != DAE && output_extension != USD && output_extension != USDA && output_extension != USDC) {
        cerr_ << "[Error] --use-element-hierarchy can be used only with .dae or .usd output.\n";
        /// @todo Lots of duplicate error-and-exit code.
		write_log(!quiet);
		print_usage();
		IfcUtil::path::delete_file(IfcUtil::path::to_utf8(output_temp_filename));
		return EXIT_FAILURE;
	}

    const bool is_tesselated = serializer->isTesselated(); // isTesselated() doesn't change at run-time
	if (!is_tesselated) {
		if (geometry_settings.get<ifcopenshell::geometry::settings::WeldVertices>().get()) {
            Logger::Notice("Weld vertices setting ignored when writing non-tesselated output");
		}
        if (geometry_settings.get<ifcopenshell::geometry::settings::GenerateUvs>().get()) {
            Logger::Notice("Generate UVs setting ignored when writing non-tesselated output");
        }
        if (center_model || center_model_geometry) {
            Logger::Notice("Centering/offsetting model setting ignored when writing non-tesselated output");
        }

		geometry_settings.get<ifcopenshell::geometry::settings::IteratorOutput>().value = ifcopenshell::geometry::settings::NATIVE;
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

	if (vmap.count("log-file")) {
		Logger::SetOutput(quiet ? nullptr : &cout_, &log_fs);
	} else {
		Logger::SetOutput(quiet ? nullptr : &cout_, vcounter.count > 1 ? &cout_ : &log_stream);
	}
	
    if (is_tesselated && (center_model || center_model_geometry)) {
		std::vector<double> offset(3);

		IfcGeom::Iterator tmp_context_iterator(geometry_kernel, geometry_settings, ifc_file, filter_funcs, num_threads);
			
		time_t start, end;
		time(&start);
		if (!quiet) Logger::Status("Computing bounds...");

		if (center_model_geometry) {
			if (!tmp_context_iterator.initialize()) {
				/// @todo It would be nice to know and print separate error prints for a case where we found no entities
				/// and for a case we found no entities that satisfy our filtering criteria.
				Logger::Notice("No geometrical elements found or none successfully converted");
				serializer.reset();
				IfcUtil::path::delete_file(IfcUtil::path::to_utf8(output_temp_filename));
				write_log(!quiet);
				return EXIT_FAILURE;
			}
		}
		
        tmp_context_iterator.compute_bounds(center_model_geometry);

		time(&end);
        if (!quiet) Logger::Status("Done ! Bounds computed in " + format_duration(start, end));

        auto center = (tmp_context_iterator.bounds_min().ccomponents() + tmp_context_iterator.bounds_max().ccomponents()) * 0.5;
        offset[0] = -center(0);
        offset[1] = -center(1);
        offset[2] = -center(2);

        std::stringstream msg;
        msg << std::setprecision (std::numeric_limits< double >::max_digits10) << "Using model offset (" << offset[0] << "," << offset[1] << "," << offset[2] << ")";
        Logger::Notice(msg.str());

		geometry_settings.get<ifcopenshell::geometry::settings::ModelOffset>().value = offset;
    }

	// backwards compatibility
	if (vmap.count("plan") && vmap.count("model")) {
		geometry_settings.get<ifcopenshell::geometry::settings::OutputDimensionality>().value = ifcopenshell::geometry::settings::CURVES_SURFACES_AND_SOLIDS;
	} else if (vmap.count("model")) {
		geometry_settings.get<ifcopenshell::geometry::settings::OutputDimensionality>().value = ifcopenshell::geometry::settings::SURFACES_AND_SOLIDS;
	} else if (vmap.count("plan")) {
		geometry_settings.get<ifcopenshell::geometry::settings::OutputDimensionality>().value = ifcopenshell::geometry::settings::CURVES;
	}

	std::unique_ptr<IfcGeom::Iterator> context_iterator;
	if (!elems_from_adaptor) {
		context_iterator.reset(new IfcGeom::Iterator(geometry_kernel, geometry_settings, ifc_file, filter_funcs, num_threads));
	}	

#if defined(WITH_HDF5) && defined(IFOPSH_WITH_OPENCASCADE)
	std::unique_ptr<HdfSerializer> cache;
	if (context_iterator && vmap.count("cache-file") || vmap.count("cache")) {
		if (!vmap.count("cache-file")) {
			cache_file = input_filename + CACHE + HDF;
		}
		cache.reset(new HdfSerializer(IfcUtil::path::to_utf8(cache_file), geometry_settings, serializer_settings));
		context_iterator->set_cache(cache.get());
	}
#endif

	Logger::Message(Logger::LOG_PERF, "file geometry conversion");

    if (context_iterator && !context_iterator->initialize()) {
        /// @todo It would be nice to know and print separate error prints for a case where we found no entities
        /// and for a case we found no entities that satisfy our filtering criteria.
        Logger::Notice("No geometrical elements found or none successfully converted");
		serializer.reset();
		IfcUtil::path::delete_file(IfcUtil::path::to_utf8(output_temp_filename));
        write_log(!quiet);
        return EXIT_FAILURE;
    }

	serializer->setFile(ifc_file);

#ifdef IFOPSH_WITH_OPENCASCADE
	if (output_extension == SVG) {
		// @todo turn these all into proper settings
		if (vmap.count("section-height-from-storeys") != 0) {
			if (vmap.count("section-height")) {
				static_cast<SvgSerializer*>(serializer.get())->setSectionHeightsFromStoreys(section_height);
			} else {
				static_cast<SvgSerializer*>(serializer.get())->setSectionHeightsFromStoreys();
			}
		} else if (vmap.count("section-height") != 0) {
			Logger::Notice("Overriding section height");
			static_cast<SvgSerializer*>(serializer.get())->setSectionHeight(section_height);
		}
		if (vmap.count("print-space-names") != 0) {
			static_cast<SvgSerializer*>(serializer.get())->setPrintSpaceNames(true);
		}
		if (vmap.count("print-space-areas") != 0) {
			static_cast<SvgSerializer*>(serializer.get())->setPrintSpaceAreas(true);
		}
		if (vmap.count("draw-storey-heights") != 0) {
			static_cast<SvgSerializer*>(serializer.get())->setDrawStoreyHeights(svg_storey_height_display);
		}		
		if (bounding_width.is_initialized() && bounding_height.is_initialized()) {
			static_cast<SvgSerializer*>(serializer.get())->setBoundingRectangle(bounding_width.get(), bounding_height.get());
		}
		if (vmap.count("door-arcs")) {
			static_cast<SvgSerializer*>(serializer.get())->setDrawDoorArcs(true);
		}
		if (vmap.count("scale")) {
			int s0, s1;
			if (sscanf(svg_scale.c_str(), "%u:%u", &s0, &s1) == 2 && s0 > 0 && s1 > 0) {
				static_cast<SvgSerializer*>(serializer.get())->setScale((double)s0 / s1);
			} else {
				cerr_ << "[Error] Invalid use of --scale" << std::endl;
				print_options(serializer_options);
				return EXIT_FAILURE;
			}
		}
		if (vmap.count("section-ref")) {
			static_cast<SvgSerializer*>(serializer.get())->setSectionRef(section_ref);
		}
		if (vmap.count("elevation-ref")) {
			static_cast<SvgSerializer*>(serializer.get())->setElevationRef(elevation_ref);
		}
		if (vmap.count("elevation-ref-guid")) {
			static_cast<SvgSerializer*>(serializer.get())->setElevationRefGuid(elevation_ref_guid);
		}
		if (vmap.count("auto-section")) {
			static_cast<SvgSerializer*>(serializer.get())->setAutoSection(true);
		}
		if (vmap.count("auto-elevation")) {
			static_cast<SvgSerializer*>(serializer.get())->setAutoElevation(true);
		}
		static_cast<SvgSerializer*>(serializer.get())->setUseNamespace(vmap.count("svg-xmlns") > 0);
		static_cast<SvgSerializer*>(serializer.get())->setUseHlrPoly(vmap.count("svg-poly") > 0);
		static_cast<SvgSerializer*>(serializer.get())->setUsePrefiltering(vmap.count("svg-prefilter") > 0);
		static_cast<SvgSerializer*>(serializer.get())->setSegmentProjection(vmap.count("svg-segment-projection") > 0);
		static_cast<SvgSerializer*>(serializer.get())->setPolygonal(vmap.count("svg-write-poly") > 0);
		static_cast<SvgSerializer*>(serializer.get())->setAlwaysProject(vmap.count("svg-project") > 0);
		static_cast<SvgSerializer*>(serializer.get())->setWithoutStoreys(vmap.count("svg-without-storeys") > 0);
		static_cast<SvgSerializer*>(serializer.get())->setNoCSS(vmap.count("svg-no-css") > 0);
		if (relative_center_x && relative_center_y) {
			static_cast<SvgSerializer*>(serializer.get())->setDrawingCenter(*relative_center_x, *relative_center_y);
		}
		if (vmap.count("storey-height-line-length")) {
			static_cast<SvgSerializer*>(serializer.get())->setStoreyHeightLineLength(
				vmap["storey-height-line-length"].as<double>()
			);
		}
		if (vmap.count("space-name-transform")) {
			static_cast<SvgSerializer*>(serializer.get())->setSpaceNameTransform(
				vmap["space-name-transform"].as<std::string>()
			);
		}		
	}
#endif

    if (context_iterator && geometry_settings.get<ifcopenshell::geometry::settings::ConvertBackUnits>().get()) {
		serializer->setUnitNameAndMagnitude(context_iterator->unit_name(), static_cast<float>(context_iterator->unit_magnitude()));
	} else {
		serializer->setUnitNameAndMagnitude("METER", 1.0f);
	}

	serializer->writeHeader();

	int old_progress = quiet ? 0 : -1;

	if (!quiet) {
		Logger::Status("Creating geometry...");
	}

	// The functions IfcGeom::Iterator::get() and IfcGeom::Iterator::next() 
	// wrap an iterator of all geometrical products in the Ifc file. 
	// IfcGeom::Iterator::get() returns an IfcGeom::TriangulationElement or 
	// -BRepElement pointer, based on current settings. (see Iterator.h 
	// for definition) IfcGeom::Iterator::next() is used to poll whether more 
	// geometrical entities are available. None of these functions throw 
	// exceptions, neither for parsing errors or geometrical errors. Upon 
	// calling next() the entity to be returned has already been processed, a 
	// non-null return value guarantees that a successfully processed product is 
	// available. 
	size_t num_created = 0;

	std::list<IfcGeom::Element*>::const_iterator elems_from_adaptor_it;
	if (elems_from_adaptor) {
		elems_from_adaptor_it = elems_from_adaptor->begin();
	}
	
	while (true) {
		
        IfcGeom::Element* geom_object = elems_from_adaptor ? *elems_from_adaptor_it : context_iterator->get();

		if (is_tesselated)
		{
			serializer->write(static_cast<const IfcGeom::TriangulationElement*>(geom_object));
		}
		else
		{
			serializer->write(static_cast<const IfcGeom::BRepElement*>(geom_object));
		}

        if (!no_progress) {
			int progress = context_iterator ? context_iterator->progress() : (int)std::distance(elems_from_adaptor->cbegin(), elems_from_adaptor_it) * 100 / elems_from_adaptor->size();
			if (quiet) {
				for (; old_progress < progress; ++old_progress) {
					cout_ << ".";
					if (stderr_progress)
						cerr_ << ".";
				}
				cout_ << std::flush;
				if (stderr_progress)
					cerr_ << std::flush;
			} else if (vcounter.count == 2) {
				Logger::Message(Logger::LOG_DEBUG, "Progress " + boost::lexical_cast<std::string>(progress));
			} else {
				progress = progress / 2;
				if (old_progress != progress) Logger::ProgressBar(progress);
				old_progress = progress;
			}
        }

		++num_created;
		if (context_iterator) {
			if (!context_iterator->next()) {
				break;
			}
		} else {
			++elems_from_adaptor_it;
			if (elems_from_adaptor_it == elems_from_adaptor->end()) {
				break;
			}
		}
    } 
	if (!no_progress && quiet) {
		for (; old_progress < 100; ++old_progress) {
			cout_ << ".";
			if (stderr_progress)
				cerr_ << ".";
		}
		cout_ << std::flush;
		if (stderr_progress) {
			cerr_ << std::flush;
		}
	} else {
		const std::string task = ((num_threads == 1) ? "creating" : "writing");
		Logger::Status("\rDone " + task + " geometry (" + boost::lexical_cast<std::string>(num_created) +
			" objects)                                ");
	}

    serializer->finalize();
    // Make sure the dtor is explicitly run here (e.g. output files are closed before renaming them).
    serializer.reset();

	Logger::Message(Logger::LOG_PERF, "done file geometry conversion");

	bool successful;
	if(output_extension == USD || output_extension == USDC || output_extension == USDA) {
		// No need to rename the file
		successful = true;
	}
	else {
		// Renaming might fail (e.g. maybe the existing file was open in a viewer application)
    	// Do not remove the temp file as user can salvage the conversion result from it.
		successful = IfcUtil::path::rename_file(IfcUtil::path::to_utf8(output_temp_filename), IfcUtil::path::to_utf8(output_filename));
	}

    if (!successful) {
        cerr_ << "Unable to write output file '" << output_filename << "', see '" <<
            output_temp_filename << "' for the conversion result.";
    }

	if (geometry_settings.get<ifcopenshell::geometry::settings::ValidateQuantities>().get() && Logger::MaxSeverity() >= Logger::LOG_ERROR) {
		Logger::Error("Errors encountered during processing.");
		successful = false;
	}

	if (Logger::Verbosity() == Logger::LOG_PERF) {
		Logger::PrintPerformanceStats();
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

#include <boost/algorithm/string/predicate.hpp>

bool init_input_file(const std::string& filename, IfcParse::IfcFile*& ifc_file, bool no_progress, bool mmap) {
    time_t start, end;

    // Prevent IfcFile::Init() prints by setting output to null temporarily
    if (no_progress) { Logger::SetOutput(NULL, &log_stream); }

    time(&start);

#ifdef WITH_IFCXML
	if (boost::ends_with(boost::to_lower_copy(filename), ".ifcxml")) {
		ifc_file = IfcParse::parse_ifcxml(filename);
	} else
#endif

	{
#ifdef USE_MMAP
		ifc_file = new IfcParse::IfcFile(filename, mmap);
#else
		(void)mmap;
		ifc_file = new IfcParse::IfcFile(filename);
#endif
	}

	if (!ifc_file || !ifc_file->good()) {
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
    } else if (type == "attribute" || type == "arg") {
        filter.type = geom_filter::ENTITY_ARG;
        filter.arg = *(values.begin() + 1);
    } else {
        throw po::validation_error(po::validation_error::invalid_option_value);
    }
    filter.values.insert(values.begin() + (filter.type == geom_filter::ENTITY_ARG ? 2 : 1), values.end());
}

void validate(boost::any& v, const std::vector<std::string>& values, verbosity_counter*, long) {
	if (v.empty()) v = verbosity_counter{ 1 };
	else ++boost::any_cast<verbosity_counter&>(v).count;
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
    for(auto& f: filters) {
        if (f.type == geom_filter::ENTITY_TYPE) {
            entity_filter.include = f.include;
            entity_filter.traverse = f.traverse;
			entity_filter.entity_names = f.values;
        } else if (f.type == geom_filter::LAYER_NAME) {
            layer_filter.include = f.include;
            layer_filter.traverse = f.traverse;
            layer_filter.populate(f.values);
        } else if (f.type == geom_filter::ENTITY_ARG) {
			attribute_filter.include = f.include;
			attribute_filter.traverse = attribute_filter.traverse_openings = f.traverse;
			attribute_filter.attribute_name = f.arg;
			attribute_filter.populate(f.values);
        }
    }

    // If no entity names are specified these are the defaults to skip from output
    if (entity_filter.entity_names.empty()) {
        std::set<std::string> entities;
        entities.insert("IfcSpace");
        if (output_extension == ".svg") {
            entity_filter.include = true;
        } else {
            entities.insert("IfcOpeningElement");
        }
        entity_filter.entity_names = entities;
    }

    if (!layer_filter.values.empty()) { filter_funcs.push_back(boost::ref(layer_filter));  }
    if (!entity_filter.entity_names.empty()) { filter_funcs.push_back(boost::ref(entity_filter)); }
    if (!attribute_filter.values.empty()) { filter_funcs.push_back(boost::ref(attribute_filter)); }

    return filter_funcs;
}

namespace latebound_access {

	template <typename T>
	void set(IfcUtil::IfcBaseClass* inst, const std::string& attr, T t);

	template <typename T>
	void set_enumeration(IfcUtil::IfcBaseClass*, const std::string&, const IfcParse::enumeration_type*, T) {}

	template <>
	void set_enumeration(IfcUtil::IfcBaseClass* inst, const std::string& attr, const IfcParse::enumeration_type* enum_type, std::string t) {
		std::vector<std::string>::const_iterator it = std::find(
			enum_type->enumeration_items().begin(),
			enum_type->enumeration_items().end(),
			t);

		return set(inst, attr, EnumerationReference(enum_type, it - enum_type->enumeration_items().begin()));
	}

	template <typename T>
	void set(IfcUtil::IfcBaseClass* inst, const std::string& attr, T t) {
		auto decl = inst->declaration().as_entity();
		auto i = decl->attribute_index(attr);

		auto attr_type = decl->attribute_by_index(i)->type_of_attribute();
		if (attr_type->as_named_type() && attr_type->as_named_type()->declared_type()->as_enumeration_type() && !std::is_same<T, EnumerationReference>::value) {
			set_enumeration(inst, attr, attr_type->as_named_type()->declared_type()->as_enumeration_type(), t);
		} else {
			inst->set_attribute_value(i, t);
		}
	}

	IfcUtil::IfcBaseClass* create(IfcParse::IfcFile& f, const std::string& entity) {
		auto decl = f.schema()->declaration_by_name(entity);
		auto data = IfcEntityInstanceData(storage_t(decl->as_entity()->attribute_count()));
		auto inst = f.schema()->instantiate(decl, std::move(data));
		if (decl->is("IfcRoot")) {
			IfcParse::IfcGlobalId guid;
			latebound_access::set(inst, "GlobalId", (std::string) guid);
		}
		return f.addEntity(inst);
	}
}

void fix_quantities(IfcParse::IfcFile& f, bool no_progress, bool quiet, bool stderr_progress) {
	{
		auto delete_reversed = [&f](const aggregate_of_instance::ptr& insts) {
			if (!insts) {
				return;
			}
			// Lists are traversed back to front as the list may be mutated when
			// instances are removed from the grouping by type.
			for (auto it = insts->end() - 1; it >= insts->begin(); --it) {
				IfcUtil::IfcBaseClass* const inst = *it;
				f.removeEntity(inst);
			}
		};

		// Delete quantities
		auto quantities = f.instances_by_type("IfcPhysicalQuantity");
		if (quantities) {
			quantities = quantities->filtered({ f.schema()->declaration_by_name("IfcPhysicalComplexQuantity") });
			delete_reversed(quantities);
		}

		// Delete complexes
		delete_reversed(f.instances_by_type("IfcPhysicalComplexQuantity"));

		auto element_quantities = f.instances_by_type("IfcElementQuantity");

		// Capture relationship nodes
		std::vector<IfcUtil::IfcBaseClass*> relationships;
		auto IfcRelDefinesByProperties = f.schema()->declaration_by_name("IfcRelDefinesByProperties");
		if (element_quantities) {
			for (auto& eq : *element_quantities) {
				auto rels = eq->file_->getInverse(eq->id(), IfcRelDefinesByProperties, -1);
				for (auto& rel : *rels) {
					relationships.push_back(rel);
				}
			}

			// Delete element quantities
			delete_reversed(element_quantities);
		}


		// Delete relationship nodes
		for (auto& rel : relationships) {
			f.removeEntity(rel);
		}
	}

	ifcopenshell::geometry::Settings settings;
	settings.get<ifcopenshell::geometry::settings::UseWorldCoords>().value = false;
	settings.get<ifcopenshell::geometry::settings::WeldVertices>().value = false;
	settings.get<ifcopenshell::geometry::settings::ReorientShells>().value = true;
	settings.get<ifcopenshell::geometry::settings::ConvertBackUnits>().value = true;
	settings.get<ifcopenshell::geometry::settings::IteratorOutput>().value = ifcopenshell::geometry::settings::NATIVE;

	IfcGeom::Iterator context_iterator(settings, &f, {}, 1);

	if (!context_iterator.initialize()) {
		return;
	}

	size_t num_created = 0;
	int old_progress = quiet ? 0 : -1;

	auto person = latebound_access::create(f, "IfcPerson");
	latebound_access::set(person, "FamilyName", std::string("IfcOpenShell"));
	latebound_access::set(person, "GivenName", std::string("IfcOpenShell"));
	
	auto org = latebound_access::create(f, "IfcOrganization");
	latebound_access::set(org, "Name", std::string("IfcOpenShell"));
	
	auto pando = latebound_access::create(f, "IfcPersonAndOrganization");
	latebound_access::set(pando, "ThePerson", person);
	latebound_access::set(pando, "TheOrganization", org);
	
	auto application = latebound_access::create(f, "IfcApplication");
	latebound_access::set(application, "ApplicationDeveloper", org);
	latebound_access::set(application, "Version", std::string(IFCOPENSHELL_VERSION));
	latebound_access::set(application, "ApplicationFullName", std::string("IfcConvert"));
	latebound_access::set(application, "ApplicationIdentifier", std::string("IfcConvert" IFCOPENSHELL_VERSION));
	
	auto ownerhist = latebound_access::create(f, "IfcOwnerHistory");
	latebound_access::set(ownerhist, "OwningUser", pando);
	latebound_access::set(ownerhist, "OwningApplication", application);
	latebound_access::set(ownerhist, "ChangeAction", std::string("MODIFIED"));
	latebound_access::set(ownerhist, "CreationDate", (int)time(0));

	IfcUtil::IfcBaseClass* quantity = nullptr;
	aggregate_of_instance::ptr objects;
	boost::shared_ptr<IfcGeom::Representation::BRep> previous_geometry_pointer;

	for (;; ++num_created) {
		bool has_more = true;
		if (num_created) {
			has_more = context_iterator.next();
		}
		IfcGeom::BRepElement* geom_object = nullptr;
		if (has_more) {
			geom_object = context_iterator.get_native();
		}

		if (geom_object && geom_object->geometry_pointer() == previous_geometry_pointer) {
			// @todo
			objects->push(const_cast<IfcUtil::IfcBaseEntity*>(geom_object->product()));
		} else {
			if (quantity) {
				auto rel = latebound_access::create(f, "IfcRelDefinesByProperties");
				latebound_access::set(rel, "OwnerHistory", ownerhist);
				latebound_access::set(rel, "RelatedObjects", objects);
				latebound_access::set(rel, "RelatingPropertyDefinition", quantity);
			}

			if (!geom_object) {
				break;
			}

			aggregate_of_instance::ptr quantities(new aggregate_of_instance);

			double a, b, c;
			if (geom_object->geometry().calculate_surface_area(a)) {
				auto quantity_area = latebound_access::create(f, "IfcQuantityArea");
				latebound_access::set(quantity_area, "Name", std::string("Total Surface Area"));
				latebound_access::set(quantity_area, "AreaValue", a);
				quantities->push(quantity_area);
			}
			
			if (geom_object->geometry().calculate_volume(a)) {
				auto quantity_volume = latebound_access::create(f, "IfcQuantityVolume");
				latebound_access::set(quantity_volume, "Name", std::string("Volume"));
				latebound_access::set(quantity_volume, "VolumeValue", a);
				quantities->push(quantity_volume);
			}

			if (geom_object->calculate_projected_surface_area(a, b, c)) {
				auto quantity_area = latebound_access::create(f, "IfcQuantityArea");
				latebound_access::set(quantity_area, "Name", std::string("Footprint Area"));
				latebound_access::set(quantity_area, "AreaValue", c);
				quantities->push(quantity_area);
			}

			auto quantity_complex = latebound_access::create(f, "IfcPhysicalComplexQuantity");
			latebound_access::set(quantity_complex, "Name", std::string("Shape Validation Properties"));
			quantities->push(quantity_complex);

			aggregate_of_instance::ptr quantities_2(new aggregate_of_instance);

			for (auto& part : geom_object->geometry()) {				
				auto quantity_count = latebound_access::create(f, "IfcQuantityCount");
				latebound_access::set(quantity_count, "Name", std::string("Surface Genus"));
				latebound_access::set(quantity_count, "Description", '#' + boost::lexical_cast<std::string>(part.ItemId()));
				latebound_access::set(quantity_count, "CountValue", part.Shape()->surface_genus());

				quantities_2->push(quantity_count);				
			}

			latebound_access::set(quantity_complex, "HasQuantities", quantities_2);

			if (quantities->size()) {
				quantity = latebound_access::create(f, "IfcElementQuantity");
				latebound_access::set(quantity, "OwnerHistory", ownerhist);
				latebound_access::set(quantity, "Quantities", quantities);
			}

			objects.reset(new aggregate_of_instance);
			// @todo
			objects->push(const_cast<IfcUtil::IfcBaseEntity*>(geom_object->product()));
		}

		previous_geometry_pointer = geom_object->geometry_pointer();

		if (!no_progress) {
			if (quiet) {
				const int progress = context_iterator.progress();
				for (; old_progress < progress; ++old_progress) {
					std::cout << ".";
					if (stderr_progress)
						cerr_ << ".";
				}
				std::cout << std::flush;
				if (stderr_progress)
					cerr_ << std::flush;
			} else {
				const int progress = context_iterator.progress() / 2;
				if (old_progress != progress) Logger::ProgressBar(progress);
				old_progress = progress;
			}
		}
	}

	if (!no_progress && quiet) {
		for (; old_progress < 100; ++old_progress) {
			std::cout << ".";
			if (stderr_progress)
				cerr_ << ".";
		}
		std::cout << std::flush;
		if (stderr_progress)
			cerr_ << std::flush;
	} else {
		Logger::Status("\rDone writing quantities for " + boost::lexical_cast<std::string>(num_created) +
			" objects                                ");
	}

}
