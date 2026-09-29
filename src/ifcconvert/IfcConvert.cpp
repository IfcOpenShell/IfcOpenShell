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

#include "../serializers/document_serializer_plugin.h"
#include "../serializers/geometry_serializer_plugin.h"

#include "../ifcgeom/filter.h"
#include "../ifcgeom/iterator.h"
#include "../ifcgeom/render_styles.h"
#include "../ifcgeom/hybrid_kernel.h"

#include "../ifcparse/utils.h"

#include <boost/program_options.hpp>
#include <memory>
#include <boost/optional/optional_io.hpp>

#include <algorithm>
#include <fstream>
#include <functional>
#include <iomanip>
#include <map>
#include <set>
#include <sstream>
#include <time.h>

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

namespace {

struct serializer_usage_line {
	std::string extensions;
	std::string name;
	std::string description;
};

std::string join_extensions(const std::vector<std::string>& extensions) {
	std::ostringstream stream;
	for (std::size_t i = 0; i < extensions.size(); ++i) {
		if (i != 0) {
			stream << ", ";
		}
		stream << extensions[i];
	}
	return stream.str();
}

void print_serializer_section(const char* title, std::vector<serializer_usage_line> lines) {
	if (lines.empty()) {
		return;
	}

	std::size_t extensions_width = 0;
	std::size_t name_width = 0;
	for (const auto& line : lines) {
		extensions_width = std::max(extensions_width, line.extensions.size());
		name_width = std::max(name_width, line.name.size());
	}

	cout_ << title << "\n";
	for (const auto& line : lines) {
		const auto extensions = ifcopenshell::path::from_utf8(line.extensions);
		const auto name = ifcopenshell::path::from_utf8(line.name);
		const auto description = ifcopenshell::path::from_utf8(line.description);
		cout_ << "  "
			<< std::left << std::setw(static_cast<int>(extensions_width + 2)) << extensions
			<< std::setw(static_cast<int>(name_width + 2)) << name
			<< description << "\n";
	}
	cout_ << "\n";
}

std::vector<serializer_usage_line> geometry_serializer_usage_lines() {
	auto serializers = ifcopenshell::serializers::geometry_serializer_registry_instance().serializers();
	std::sort(serializers.begin(), serializers.end(), [](const auto& a, const auto& b) {
		const auto& lhs = a.extensions.empty() ? a.format : a.extensions.front();
		const auto& rhs = b.extensions.empty() ? b.format : b.extensions.front();
		if (lhs != rhs) {
			return lhs < rhs;
		}
		return a.format < b.format;
	});

	std::vector<serializer_usage_line> lines;
	lines.reserve(serializers.size());
	for (const auto& info : serializers) {
		lines.push_back({ join_extensions(info.extensions), info.name, info.description });
	}
	return lines;
}

std::vector<serializer_usage_line> document_serializer_usage_lines() {
	auto serializers = ifcopenshell::serializers::document_serializer_registry_instance().serializers();
	std::sort(serializers.begin(), serializers.end(), [](const auto& a, const auto& b) {
		if (a.format != b.format) {
			return a.format < b.format;
		}
		return a.schema_name < b.schema_name;
	});

	std::set<std::string> seen_formats;
	std::vector<serializer_usage_line> lines;
	for (const auto& info : serializers) {
		if (!seen_formats.insert(info.format).second) {
			continue;
		}
		lines.push_back({ "." + info.format, info.name, info.description });
	}
	return lines;
}

}

void print_version()
{
	// @todo print plug-in versions
    cout_ << "IfcOpenShell IfcConvert " << IFCOPENSHELL_VERSION << "\n";
}

void print_usage(bool suggest_help = true)
{
    cout_ << "Usage: IfcConvert [options] <input.ifc> [<output>]\n"
        << "\n"
        << "Converts (the geometry in) an IFC file into one of the following formats:\n\n";
	print_serializer_section("Geometry serializers:", geometry_serializer_usage_lines());
	print_serializer_section("Document serializers:", document_serializer_usage_lines());
	print_serializer_section("Built-in:", { { ".ifc", "IFC-SPF", "Industry Foundation Classes." } });
	cout_
        << "If no output filename given, <input>" << ifcopenshell::path::from_utf8(DEFAULT_EXTENSION) << " will be used as the output file.\n";
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
    std::ifstream file(ifcopenshell::path::from_utf8(filename).c_str());
    return file.good();
}

static std::basic_stringstream<path_t::value_type> log_stream;
void write_log(bool);
void fix_quantities(ifcopenshell::file&, bool, bool, bool, ifcopenshell::logger& logger = ifcopenshell::logger::root());
std::string format_duration(time_t start, time_t end);

/// @todo make the filters non-global
ifcopenshell::geom::entity_filter entity_filter; // Entity filter is used always by default.
ifcopenshell::geom::layer_filter layer_filter;
ifcopenshell::geom::attribute_filter attribute_filter;

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
std::vector<ifcopenshell::geom::filter_function> setup_filters(const std::vector<geom_filter>&, const std::string&);

bool init_input_file(const std::string& filename, ifcopenshell::file*& ifc_file, bool no_progress, bool mmap, bool bypass_properties=false, ifcopenshell::logger& logger = ifcopenshell::logger::root());

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
	ifcopenshell::logger logger;

	inclusion_filter include_filter;
	inclusion_traverse_filter include_traverse_filter;
	exclusion_filter exclude_filter;
	exclusion_traverse_filter exclude_traverse_filter;
	path_t filter_filename;
	path_t default_material_filename;
	path_t log_file;
	std::string log_format;
	std::string geometry_kernel;
	auto& document_serializer_registry = ifcopenshell::serializers::document_serializer_registry_instance();
	auto& geometry_serializer_registry = ifcopenshell::serializers::geometry_serializer_registry_instance();

    po::options_description generic_options("Command line options");
	verbosity_counter vcounter;
	generic_options.add_options()
		("help,h", "display usage information")
		("version", "display version information")
		("verbose,v", po::value(&vcounter)->zero_tokens(), "more verbose log messages. Use twice (-vv) for debugging level.")
		("quiet,q", "less status and progress output")
		("stderr-progress", "output progress to stderr stream")
		("yes,y", "answer 'yes' automatically to possible confirmation queries (e.g. overwriting an existing output file)")
		("no-progress", "suppress possible progress bar type of prints that use carriage return")
		("fail-on-error", "return a non-zero exit code when one or more errors were logged during "
			"geometry conversion (e.g. an element failed to convert). By default IfcConvert exits "
			"successfully as long as an output file could be written, even if some elements were "
			"silently dropped. Enable this flag so scripts and CI can detect partial conversions.")
		("log-format", po::value<std::string>(&log_format), "log format: plain or json")
		("log-file", new po::typed_value<path_t, char_t>(&log_file), "redirect log output to file");

    po::options_description fileio_options;
	fileio_options.add_options()
#ifdef USE_MMAP
		("mmap", "use memory-mapped file for input")
#endif
		("input-file", new po::typed_value<path_t, char_t>(0), "input IFC file")
		("output-file", new po::typed_value<path_t, char_t>(0), "output geometry file")
		("stream", "Use streaming conversion when supported (RocksDB uses it automatically)")
		;

	po::options_description ifc_options("IFC options");
	ifc_options.add_options()
		("calculate-quantities", "Calculate or fix the physical quantity definitions "
			"based on an interpretation of the geometry when exporting IFC");

	int num_threads;
	std::string offset_str, rotation_str;

	std::string default_kernel;
#ifdef IFOPSH_WITH_MANIFOLD
	default_kernel = "manifold";
#endif
#ifdef IFOPSH_WITH_CGAL
	default_kernel = "cgal";
#endif
#ifdef IFOPSH_WITH_OPENCASCADE
	default_kernel = "opencascade";
#endif

	// none, convex-decomposition, minkowski-triangles or halfspace-snapping
	std::string exterior_only_algo;

	ifcopenshell::geom::settings settings;

	po::options_description geom_options("Geometry options");
	geom_options.add_options()
		("kernel", po::value<std::string>(&geometry_kernel)->default_value(default_kernel),
			"Geometry kernel to use (opencascade, cgal, cgal-simple, manifold, passthrough, hybrid-cgal-simple-opencascade, hybrid-passthrough-opencascade).")
		("threads,j", po::value<int>(&num_threads)->default_value(1),
			"Number of parallel processing threads for geometry interpretation.")
		("center-model",
            "Centers the elements by applying the center point of all placements as an offset."
            "Can take several minutes on large models.")
		("center-model-geometry",
            "Centers the elements by applying the center point of all mesh vertices as an offset.")
		("model-offset", po::value<std::string>(&offset_str),
			"Applies an arbitrary offset of form 'x;y;z' to all placements.")
		("model-rotation", po::value<std::string>(&rotation_str),
			"Applies an arbitrary quaternion rotation of form 'x;y;z;w' to all placements.")
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

	settings.define_options(geom_options);

    std::string bounds;
#ifdef HAVE_ICU
    std::string unicode_mode;
#endif
    po::options_description serializer_options("Serialization options");
    serializer_options.add_options()
#ifdef HAVE_ICU
        ("unicode", po::value<std::string>(&unicode_mode),
            "Specifies the Unicode handling behavior when parsing the IFC file. "
            "Accepted values 'utf8' (the default) and 'escape'.")
#endif
		;

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
        cerr_ << "[error] Unknown option '" << e.get_option_name().c_str() << "'\n\n";
        print_usage();
        return EXIT_FAILURE;
    } catch (const po::error_with_option_name& e) {
        cerr_ << "[error] Invalid usage of '" << e.get_option_name().c_str() << "': " << e.what() << "\n\n";
        return EXIT_FAILURE;
    } catch (const std::exception& e) {
        cerr_ << "[error] " << e.what() << "\n\n";
        print_usage();
        return EXIT_FAILURE;
    } catch (...) {
		cerr_ << "[error] Unknown error parsing command line options\n\n";
        print_usage();
        return EXIT_FAILURE;
    }

    po::notify(vmap);

	const bool mmap = vmap.count("mmap") != 0;
	const bool no_progress = vmap.count("no-progress") != 0;
	const bool fail_on_error = vmap.count("fail-on-error") != 0;
	const bool quiet = vmap.count("quiet") != 0;
	const bool stderr_progress = vmap.count("stderr-progress") != 0;

	const bool center_model = vmap.count("center-model") != 0;
	const bool center_model_geometry = vmap.count("center-model-geometry") != 0;
	const bool model_offset = vmap.count("model-offset") != 0;
	const bool model_rotation = vmap.count("model-rotation") != 0;

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
        cerr_ << "[error] Input file not specified" << std::endl;
        print_usage();
        return EXIT_FAILURE;
    }

	if (num_threads <= 0) {
		num_threads = std::thread::hardware_concurrency();
		logger.notice("SYS", 7, "Using " + std::to_string(num_threads) + " threads");
	}

	if (vmap.count("log-format") == 1) {
		boost::to_lower(log_format);
		if (log_format == "plain") {
			logger.output_format(ifcopenshell::logger::FMT_PLAIN);
		} else if (log_format == "json") {
			logger.output_format(ifcopenshell::logger::FMT_JSON);
		} else {
			cerr_ << "[error] --log-format should be either plain or json" << std::endl;
			print_usage();
			return EXIT_FAILURE;
		}
	}

    if (!filter_filename.empty()) {
        size_t num_filters = read_filters_from_file(ifcopenshell::path::to_utf8(filter_filename), include_filter, include_traverse_filter, exclude_filter, exclude_traverse_filter);
        if (num_filters) {
            logger.notice("SYS", 8, boost::lexical_cast<std::string>(num_filters) + " filters read from specifified file.");
        } else {
            cerr_ << "[error] No filters read from specifified file.\n";
            return EXIT_FAILURE;
        }
    }

#ifdef HAVE_ICU
    if (!unicode_mode.empty()) {
        if (unicode_mode == "utf8") {
            ifcopenshell::runtime_character_decoder::mode = ifcopenshell::runtime_character_decoder::UTF8;
        } else if (unicode_mode == "escape") {
            ifcopenshell::runtime_character_decoder::mode = ifcopenshell::runtime_character_decoder::ESCAPE;
        } else {
            cerr_ << "[error] Invalid value for --unicode" << std::endl;
            print_options(serializer_options);
            return 1;
        }
    }
#endif

    if (!default_material_filename.empty()) {
        try {
            ifcopenshell::geom::set_default_style_file(ifcopenshell::path::to_utf8(default_material_filename));
        } catch (const std::exception& e) {
            cerr_ << "[error] Could not read default material file:" << std::endl;
            cerr_ << e.what() << std::endl;
            return EXIT_FAILURE;
        }
    }

	const path_t input_filename = vmap["input-file"].as<path_t>();
    /*
	// todo also allow rocksdb dir
	if (!file_exists(ifcopenshell::path::to_utf8(input_filename))) {
        cerr_ << "[error] Input file '" << input_filename << "' does not exist" << std::endl;
        return EXIT_FAILURE;
    }*/

	// If no output filename is specified a Wavefront OBJ file will be output
	// to maintain backwards compatibility with the obsolete IfcObj executable.
	const path_t output_filename = vmap.count("output-file") == 1
		? vmap["output-file"].as<path_t>()
		: change_extension(input_filename, ifcopenshell::path::from_utf8(DEFAULT_EXTENSION));

	if (output_filename.size() < 5) {
        cerr_ << "[error] Invalid or unsupported output file '" << output_filename << "' given" << std::endl;
        print_usage();
		return EXIT_FAILURE;
	}

    if (file_exists(ifcopenshell::path::to_utf8(output_filename)) && !vmap.count("yes")) {
        std::string answer;
        cout_ << "A file '" << output_filename << "' already exists. Overwrite the existing file? y/n" << std::endl;
        std::cin >> answer;
        if (!boost::iequals(answer, "yes") && !boost::iequals(answer, "y")) {
            return EXIT_SUCCESS;
        }
    }

	ofstream_t log_fs;

	if (vmap.count("log-file")) {
		log_fs.open(log_file.c_str(), std::ios::app);
		logger.set_output(quiet ? nullptr : &cout_, &log_fs);
	} else {
		logger.set_output(quiet ? nullptr : &cout_, vcounter.count > 1 ? &cout_ : &log_stream);
	}

	switch (vcounter.count) {
	case 0:
		logger.verbosity(ifcopenshell::logger::LOG_ERROR);
		break;
	case 1:
		logger.verbosity(ifcopenshell::logger::LOG_NOTICE);
		break;
	case 2:
		logger.verbosity(ifcopenshell::logger::LOG_DEBUG);
		break;
	case 3:
		logger.verbosity(ifcopenshell::logger::LOG_PERF);
		break;
	case 4:
		logger.verbosity(ifcopenshell::logger::LOG_PERF);
		logger.print_performance_stats_on_element(true);
		break;
	}

    path_t output_temp_filename = output_filename + ifcopenshell::path::from_utf8(TEMP_FILE_EXTENSION);

	std::vector<path_t> tokens;
	split(tokens, output_filename, boost::is_any_of("."));
	std::vector<path_t>::iterator tok_iter;
	path_t ext = *(tokens.end() - 1);
	path_t dot;
	dot = '.';
	path_t output_extension = dot + ext;

	boost::to_lower(output_extension);
	const auto output_extension_utf8 = ifcopenshell::path::to_utf8(output_extension);

	ifcopenshell::file* ifc_file = 0;

    const path_t IFC = ifcopenshell::path::from_utf8(".ifc");

	auto run_document_serializer = [&](const ifcopenshell::serializers::document_serializer_info* document_serializer_info) {
		int exit_code = EXIT_FAILURE;
		try {
			const bool use_input_filename = document_serializer_info->supports_input_filename &&
				(vmap.count("stream") || !document_serializer_info->supports_ifc_file);
			if (!use_input_filename && !document_serializer_info->supports_ifc_file) {
				throw ifcopenshell::exception("Selected document serializer requires --stream");
			}

			if (use_input_filename || ifc_file || init_input_file(ifcopenshell::path::to_utf8(input_filename), ifc_file, no_progress || quiet, mmap)) {
				if (!use_input_filename) {
					document_serializer_info = document_serializer_registry.find(output_extension_utf8, ifc_file->schema()->name());
					if (!document_serializer_info) {
						throw ifcopenshell::exception("No document serializer registered for " + output_extension_utf8 + " and schema " + ifc_file->schema()->name());
					}
				}

				time_t start, end;
				time(&start);

				ifcopenshell::serializers::document_serializer_context context;
				context.file = use_input_filename ? nullptr : ifc_file;
				context.input_filename = ifcopenshell::path::to_utf8(input_filename);
				context.output_filename = ifcopenshell::path::to_utf8(document_serializer_info->writes_final_output ? output_filename : output_temp_filename);
				context.schema_name = ifc_file ? ifc_file->schema()->name() : document_serializer_info->schema_name;
				context.stream = use_input_filename;

				std::shared_ptr<ifcopenshell::geom::serializer> serializer = document_serializer_registry.create(output_extension_utf8, context);
				if (serializer->is_streaming() != use_input_filename) {
					throw ifcopenshell::exception("Selected document serializer streaming mode does not match its registry metadata");
				}
				logger.status("Writing " + boost::to_upper_copy(document_serializer_info->format) + " output...");
				serializer->finalize();
				serializer.reset();

				time(&end);
				logger.status("Done! Conversion took " +  format_duration(start, end));

				if (!document_serializer_info->writes_final_output &&
					!ifcopenshell::path::rename_file(ifcopenshell::path::to_utf8(output_temp_filename), ifcopenshell::path::to_utf8(output_filename))) {
					throw ifcopenshell::exception(
						"Unable to write output file '" + ifcopenshell::path::to_utf8(output_filename) +
						"', see '" + ifcopenshell::path::to_utf8(output_temp_filename) + "' for the conversion result");
				}
				exit_code = EXIT_SUCCESS;
			}
		} catch (const std::exception& e) {
			logger.error("SYS", 9, e);
		}
		write_log(!quiet);
		return exit_code;
	};

	const auto* document_serializer_info = document_serializer_registry.find(output_extension_utf8);
	if (document_serializer_info) {
		return run_document_serializer(document_serializer_info);
	} else if (output_extension == IFC) {
		int exit_code = EXIT_FAILURE;
		try {
			if (init_input_file(ifcopenshell::path::to_utf8(input_filename), ifc_file, no_progress || quiet, mmap, false, logger)) {
                time_t start, end;
				time(&start);
				std::ofstream fs(output_filename.c_str());
				if (fs.is_open()) {
					if (vmap.count("calculate-quantities")) {
						fix_quantities(*ifc_file, no_progress, quiet, stderr_progress, logger);
					}
					fs << *ifc_file;
					exit_code = EXIT_SUCCESS;
				} else {
					logger.error("SYS", 10, "Unable to open output file for writing");
				}
                time(&end);
                logger.status("Done! Writing IFC took " +  format_duration(start, end));
			}
		} catch (const std::exception& e) {
			logger.error("SYS", 11, e);
		}
		write_log(!quiet);
		return exit_code;
	}

	const auto* geometry_serializer_info = geometry_serializer_registry.find(output_extension_utf8);
	if (!geometry_serializer_info) {
		if (init_input_file(ifcopenshell::path::to_utf8(input_filename), ifc_file, no_progress || quiet, mmap)) {
			document_serializer_info = document_serializer_registry.find(output_extension_utf8, ifc_file->schema()->name());
			if (document_serializer_info) {
				return run_document_serializer(document_serializer_info);
			}
		}
		cerr_ << "[error] Unknown output filename extension '" << output_extension << "'\n";
		write_log(!quiet);
		print_usage();
		return EXIT_FAILURE;
	}

    /// @todo Clean up this filter code further.
    std::vector<geom_filter> used_filters;
    if (include_filter.type != geom_filter::UNUSED) { used_filters.push_back(include_filter); }
    if (include_traverse_filter.type != geom_filter::UNUSED) { used_filters.push_back(include_traverse_filter); }
    if (exclude_filter.type != geom_filter::UNUSED) { used_filters.push_back(exclude_filter); }
    if (exclude_traverse_filter.type != geom_filter::UNUSED) { used_filters.push_back(exclude_traverse_filter); }

    std::vector<ifcopenshell::geom::filter_function> filter_funcs = setup_filters(used_filters, ifcopenshell::path::to_utf8(output_extension));
    if (filter_funcs.empty()) {
        cerr_ << "[error] Failed to set up geometry filters\n";
        return EXIT_FAILURE;
    }

    if (!entity_filter.entity_names.empty()) { entity_filter.update_description(); logger.notice("SYS", 13, entity_filter.description); }
    if (!layer_filter.values.empty()) { layer_filter.update_description(); logger.notice("SYS", 14, layer_filter.description); }
	if (!attribute_filter.attribute_name.empty()) { attribute_filter.update_description(); logger.notice("SYS", 15, attribute_filter.description); }

	if (geometry_serializer_info && geometry_serializer_info->requires_ascii_temp_file) {
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

	// The OS will clean up for us if there is a leak
	settings.get<ifcopenshell::geom::settings::OcctNoCleanTriangulation>().value = true;

	if (settings.get<ifcopenshell::geom::settings::PermissiveShapeReuse>().get()) {
		settings.get<ifcopenshell::geom::settings::NoParallelMapping>().value = true;
	}

	if (vmap[ifcopenshell::geom::settings::WeldVertices::name].defaulted()) {
		settings.get<ifcopenshell::geom::settings::WeldVertices>().value = false;
	}

	if (settings.get<ifcopenshell::geom::settings::ForceSpaceTransparency>().has()) {
		ifcopenshell::geom::update_default_style("IfcSpace")->transparency = settings.get<ifcopenshell::geom::settings::ForceSpaceTransparency>().get();
	}

	if (settings.get<ifcopenshell::geom::settings::UseElementHierarchy>().get() &&
		!geometry_serializer_info->supports_user_element_hierarchy) {
		cerr_ << "[error] --use-element-hierarchy is not supported by the selected geometry serializer.\n";
		write_log(!quiet);
		print_usage();
		ifcopenshell::path::delete_file(ifcopenshell::path::to_utf8(output_temp_filename));
		return EXIT_FAILURE;
	}

	ifcopenshell::serializers::geometry_serializer_context serializer_context{
		ifcopenshell::path::to_utf8(output_filename),
		ifcopenshell::path::to_utf8(output_temp_filename),
		settings
	};

	std::shared_ptr<ifcopenshell::geom::geometry_serializer> serializer; /**< @todo use std::unique_ptr when possible */
	try {
		geometry_serializer_registry.configure(output_extension_utf8, serializer_context);
		serializer = geometry_serializer_registry.create(output_extension_utf8, serializer_context);
	} catch (const std::exception& e) {
		cerr_ << "[error] " << e.what() << std::endl;
		write_log(!quiet);
		print_options(serializer_options);
		ifcopenshell::path::delete_file(ifcopenshell::path::to_utf8(output_temp_filename));
		return EXIT_FAILURE;
	}

    const bool is_tesselated = serializer->isTesselated(); // isTesselated() doesn't change at run-time
	if (!is_tesselated) {
		if (settings.get<ifcopenshell::geom::settings::WeldVertices>().get()) {
            logger.notice("SYS", 16, "Weld vertices setting ignored when writing non-tesselated output");
		}
        if (settings.get<ifcopenshell::geom::settings::GenerateUvs>().get()) {
            logger.notice("SYS", 17, "Generate UVs setting ignored when writing non-tesselated output");
        }
        if (center_model || center_model_geometry) {
            logger.notice("SYS", 18, "Centering/offsetting model setting ignored when writing non-tesselated output");
        }

		settings.get<ifcopenshell::geom::settings::IteratorOutput>().value = ifcopenshell::geom::settings::NATIVE;
	}

	if (!serializer->ready()) {
		logger.error("SYS", 25, "Unable to open output file '" + ifcopenshell::path::to_utf8(output_filename) + "' for writing; check that the directory exists and is writable");
		ifcopenshell::path::delete_file(ifcopenshell::path::to_utf8(output_temp_filename));
		write_log(!quiet);
		return EXIT_FAILURE;
	}

	time_t start,end;
	time(&start);

	// @nb last argument true -> bypass_properties which are not read by any of the geometry serializers
    // Document serializers and IFC are already special-cased above
    // SVG requires properties for IfcAnnotation/DRAWING properties
    if (!init_input_file(ifcopenshell::path::to_utf8(input_filename), ifc_file, no_progress || quiet, mmap, geometry_serializer_info->bypass_properties, logger)) {
        write_log(!quiet);
		serializer.reset();
        ifcopenshell::path::delete_file(ifcopenshell::path::to_utf8(output_temp_filename)); /**< @todo Windows Unicode support */
        return EXIT_FAILURE;
    }

	if (vmap.count("log-file")) {
		logger.set_output(quiet ? nullptr : &cout_, &log_fs);
	} else {
		logger.set_output(quiet ? nullptr : &cout_, vcounter.count > 1 ? &cout_ : &log_stream);
	}

	if (model_rotation) {
		std::vector<double> rotation(4);
		int n = 0;
		if (sscanf(rotation_str.c_str(), "%lf;%lf;%lf;%lf %n", &rotation[0], &rotation[1], &rotation[2], &rotation[3], &n) != 4 || static_cast<std::size_t>(n) != rotation_str.size()) {
			cerr_ << "[error] Invalid use of --model-rotation\n";
			ifcopenshell::path::delete_file(ifcopenshell::path::to_utf8(output_temp_filename));
			print_options(serializer_options);
			return EXIT_FAILURE;
		}

		std::stringstream msg;
		msg << "Using model rotation (" << rotation[0] << "," << rotation[1] << "," << rotation[2] << "," << rotation[3] << ")";
		logger.notice("SYS", 19, msg.str());

		settings.get<ifcopenshell::geom::settings::ModelRotation>().value = rotation;
	}

	if (model_offset && (center_model || center_model_geometry)) {
		logger.notice("GEO", 22, "--model-offset ignored with --center-model or --center-model-geometry");
	}

	if (model_offset && !(center_model || center_model_geometry)) {
		std::vector<double> offset(3);
		int n = 0;
		if (sscanf(offset_str.c_str(), "%lf;%lf;%lf %n", &offset[0], &offset[1], &offset[2], &n) != 3 || static_cast<std::size_t>(n) != offset_str.size()) {
			cerr_ << "[error] Invalid use of --model-offset\n";
			ifcopenshell::path::delete_file(ifcopenshell::path::to_utf8(output_temp_filename));
			print_options(serializer_options);
			return EXIT_FAILURE;
		}

		std::stringstream msg;
		msg << std::setprecision(std::numeric_limits<double>::max_digits10) << "Using model offset (" << offset[0] << "," << offset[1] << "," << offset[2] << ")";
		logger.notice("SYS", 20, msg.str());

		settings.get<ifcopenshell::geom::settings::ModelOffset>().value = offset;
	}

    if (is_tesselated && (center_model || center_model_geometry)) {
		std::vector<double> offset(3);

		ifcopenshell::geom::iterator tmp_context_iterator(ifcopenshell::geom::kernels::construct(ifc_file, geometry_kernel, settings, logger), settings, ifc_file, filter_funcs, num_threads, logger);

		time_t bounds_start, bounds_end;
		time(&bounds_start);
		if (!quiet) logger.status("Computing bounds...");

		if (center_model_geometry) {
			if (!tmp_context_iterator.initialize()) {
				/// @todo It would be nice to know and print separate error prints for a case where we found no entities
				/// and for a case we found no entities that satisfy our filtering criteria.
				logger.notice("GEO", 23, "No geometrical elements found or none successfully converted");
				serializer.reset();
				ifcopenshell::path::delete_file(ifcopenshell::path::to_utf8(output_temp_filename));
				write_log(!quiet);
				return EXIT_FAILURE;
			}
		}

        tmp_context_iterator.compute_bounds(center_model_geometry);

		time(&bounds_end);
		if (!quiet) logger.status("Done ! Bounds computed in " + format_duration(bounds_start, bounds_end));

        auto center = (tmp_context_iterator.bounds_min().ccomponents() + tmp_context_iterator.bounds_max().ccomponents()) * 0.5;
        offset[0] = -center(0);
        offset[1] = -center(1);
        offset[2] = -center(2);

        std::stringstream msg;
        msg << std::setprecision (std::numeric_limits<double>::max_digits10) << "Using model offset (" << offset[0] << "," << offset[1] << "," << offset[2] << ")";
        logger.notice("SYS", 21, msg.str());

		settings.get<ifcopenshell::geom::settings::ModelOffset>().value = offset;
    }

	// backwards compatibility
	if (vmap.count("plan") && vmap.count("model")) {
		settings.get<ifcopenshell::geom::settings::OutputDimensionality>().value = ifcopenshell::geom::settings::CURVES_SURFACES_AND_SOLIDS;
	} else if (vmap.count("model")) {
		settings.get<ifcopenshell::geom::settings::OutputDimensionality>().value = ifcopenshell::geom::settings::SURFACES_AND_SOLIDS;
	} else if (vmap.count("plan")) {
		settings.get<ifcopenshell::geom::settings::OutputDimensionality>().value = ifcopenshell::geom::settings::CURVES;
	}

	std::unique_ptr<ifcopenshell::geom::iterator> context_iterator;
	context_iterator.reset(new ifcopenshell::geom::iterator(ifcopenshell::geom::kernels::construct(ifc_file, geometry_kernel, settings, logger), settings, ifc_file, filter_funcs, num_threads, logger));

	logger.message(ifcopenshell::logger::LOG_PERF, "file geometry conversion");

    if (context_iterator && !context_iterator->initialize()) {
        /// @todo It would be nice to know and print separate error prints for a case where we found no entities
        /// and for a case we found no entities that satisfy our filtering criteria.
        logger.notice("GEO", 25, "No geometrical elements found or none successfully converted");
		serializer.reset();
		ifcopenshell::path::delete_file(ifcopenshell::path::to_utf8(output_temp_filename));
        write_log(!quiet);
        return EXIT_FAILURE;
    }

	serializer->setFile(*ifc_file);

    if (context_iterator && settings.get<ifcopenshell::geom::settings::ConvertBackUnits>().get()) {
		serializer->setUnitNameAndMagnitude(context_iterator->unit_name(), static_cast<float>(context_iterator->unit_magnitude()));
	} else {
		serializer->setUnitNameAndMagnitude("METER", 1.0f);
	}

	serializer->writeHeader();

	int old_progress = quiet ? 0 : -1;

	if (!quiet) {
		logger.status("Creating geometry...");
	}

	// The functions ifcopenshell::geom::iterator::get() and ifcopenshell::geom::iterator::next()
	// wrap an iterator of all geometrical products in the Ifc file.
	// ifcopenshell::geom::iterator::get() returns an ifcopenshell::geom::triangulation_element or
	// -native_element pointer, based on current settings. (see iterator.h
	// for definition) ifcopenshell::geom::iterator::next() is used to poll whether more
	// geometrical entities are available. None of these functions throw
	// exceptions, neither for parsing errors or geometrical errors. Upon
	// calling next() the entity to be returned has already been processed, a
	// non-null return value guarantees that a successfully processed product is
	// available.
	size_t num_created = 0;

	while (true) {

		auto geom_object = context_iterator->get();

		if (is_tesselated)
		{
			serializer->write(static_cast<const ifcopenshell::geom::triangulation_element*>(geom_object.get()));
		}
		else
		{
			serializer->write(static_cast<const ifcopenshell::geom::native_element*>(geom_object.get()));
		}

        if (!no_progress) {
			int progress = context_iterator->progress();
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
				logger.message(ifcopenshell::logger::LOG_DEBUG, "SYS", 23, "Progress " + boost::lexical_cast<std::string>(progress));
			} else {
				progress = progress / 2;
				if (old_progress != progress) logger.progress_bar(progress);
				old_progress = progress;
			}
        }

		++num_created;
		if (!context_iterator->next()) {
			break;
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
		logger.status("\rDone " + task + " geometry (" + boost::lexical_cast<std::string>(num_created) +
			" objects)                                ");
	}

    serializer->finalize();
    // Make sure the dtor is explicitly run here (e.g. output files are closed before renaming them).
    serializer.reset();

	logger.message(ifcopenshell::logger::LOG_PERF, "GEO", 26, "done file geometry conversion");

	bool successful;
	if (geometry_serializer_info->writes_final_output) {
		// No need to rename the file
		successful = true;
	}
	else {
		// Renaming might fail (e.g. maybe the existing file was open in a viewer application)
    	// Do not remove the temp file as user can salvage the conversion result from it.
		successful = ifcopenshell::path::rename_file(ifcopenshell::path::to_utf8(output_temp_filename), ifcopenshell::path::to_utf8(output_filename));
	}

    if (!successful) {
        cerr_ << "Unable to write output file '" << output_filename << "', see '" <<
            output_temp_filename << "' for the conversion result.";
    }

	if (settings.get<ifcopenshell::geom::settings::ValidateQuantities>().get() && logger.max_severity() >= ifcopenshell::logger::LOG_ERROR) {
		logger.error("SYS", 24, "Errors encountered during processing.");
		successful = false;
	}

	if (fail_on_error && logger.max_severity() >= ifcopenshell::logger::LOG_ERROR) {
		logger.error("SYS", 26, "Errors encountered during processing, failing due to --fail-on-error.");
		successful = false;
	}

	if (logger.verbosity() == ifcopenshell::logger::LOG_PERF) {
		logger.print_performance_stats();
	}

	write_log(!quiet);

	time(&end);

    if (!quiet) {
        logger.status("\nConversion took " +  format_duration(start, end));
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

bool init_input_file(const std::string& filename, ifcopenshell::file*& ifc_file, bool no_progress, bool mmap, bool bypass_properties, ifcopenshell::logger& logger) {
    time_t start, end;

    // Prevent file::Init() prints by setting output to null temporarily
    if (no_progress) { logger.set_output(NULL, &log_stream); }

    time(&start);

	bool requires_init = false;

    {
        ifc_file = new ifcopenshell::file(ifcopenshell::uninitialized_tag{}, logger);
        requires_init = true;
    }

	if (bypass_properties) {
        ifc_file->bypass_type("IfcRelDefinesByProperties");
        ifc_file->bypass_type("IfcPropertySetDefinition");
        ifc_file->bypass_type("IfcProperty");
        ifc_file->bypass_type("IfcMaterialProperties");
        ifc_file->bypass_type("IfcProfileProperties");
        ifc_file->bypass_type("IfcPhysicalQuantity");
    }

#ifdef USE_MMAP
    if (mmap) {
        ifc_file->initialize(filename, mmap);
        requires_init = false;
    }
#else
    (void)mmap;
#endif
    if (requires_init) {
        ifc_file->initialize(filename);
    }

	if (!ifc_file || !ifc_file->good()) {
        logger.error("SYN", 1, "Unable to parse input file '" + filename + "'");
        return false;
    }
    time(&end);

    if (no_progress) { logger.set_output(&cout_, &log_stream); }
    else {  logger.status("Parsing input file took " + format_duration(start, end)); }

    return true;

}

bool append_filter(const std::string& type, const std::vector<std::string>& values, geom_filter& filter)
{
    geom_filter temp;
    parse_filter(temp, values);
    // Merge values only if type and arg match.
    if ((filter.type != geom_filter::UNUSED && filter.type != temp.type) || (!filter.arg.empty() && filter.arg != temp.arg)) {
        cerr_ << "[error] Multiple '" << type.c_str() << "' filters specified with different criteria\n";
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
    std::ifstream filter_file(ifcopenshell::path::from_utf8(filename).c_str());

    if (!filter_file.is_open()) {
        cerr_ << "[error] Unable to open filter file '" << ifcopenshell::path::from_utf8(filename) << "' or the file does not exist.\n";
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
                cerr_ << "[error] Invalid filtering type at line " << boost::lexical_cast<path_t>(line_number) << "\n";
                return 0;
            }
        } catch(...) {
            cerr_ << "[error] Unable to parse filter at line " << boost::lexical_cast<path_t>(line_number) << ".\n";
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

void validate(boost::any& v, const std::vector<std::string>&, verbosity_counter*, long) {
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
std::vector<ifcopenshell::geom::filter_function> setup_filters(const std::vector<geom_filter>& filters, const std::string& output_extension)
{
    std::vector<ifcopenshell::geom::filter_function> filter_funcs;
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

    if (!layer_filter.values.empty()) { filter_funcs.push_back(std::ref(layer_filter));  }
    if (!entity_filter.entity_names.empty()) { filter_funcs.push_back(std::ref(entity_filter)); }
    if (!attribute_filter.values.empty()) { filter_funcs.push_back(std::ref(attribute_filter)); }

    return filter_funcs;
}

namespace latebound_access {

	template <typename T>
	void set(express::base inst, const std::string& attr, T t);

	template <typename T>
    void set_enumeration(express::base, const std::string&, const ifcopenshell::enumeration_type*, T) {}

	template <>
    void set_enumeration(express::base inst, const std::string& attr, const ifcopenshell::enumeration_type* enum_type, std::string t) {
		std::vector<std::string>::const_iterator it = std::find(
			enum_type->enumeration_items().begin(),
			enum_type->enumeration_items().end(),
			t);

		return set(inst, attr, ifcopenshell::enumeration_reference(enum_type, it - enum_type->enumeration_items().begin()));
	}

	template <typename T>
    void set(express::base inst, const std::string& attr, T t) {
		auto decl = inst.declaration().as_entity();
		auto i = decl->attribute_index(attr);

		auto attr_type = decl->attribute_by_index(i)->type_of_attribute();
		if (attr_type->as_named_type() && attr_type->as_named_type()->declared_type()->as_enumeration_type() && !std::is_same<T, ifcopenshell::enumeration_reference>::value) {
			set_enumeration(inst, attr, attr_type->as_named_type()->declared_type()->as_enumeration_type(), t);
		} else {
			inst.set_attribute_value(i, t);
		}
	}

	express::base create(ifcopenshell::file& f, const std::string& entity) {
		auto decl = f.schema()->declaration_by_name(entity);
        return f.create(decl);
	}
}

void fix_quantities(ifcopenshell::file& f, bool no_progress, bool quiet, bool stderr_progress, ifcopenshell::logger& logger) {
	{
		auto delete_reversed = [&f](const std::vector<express::base>& insts) {
			// Lists are traversed back to front as the list may be mutated when
			// instances are removed from the grouping by type.
			for (auto it = insts.end() - 1; it >= insts.begin(); --it) {
                f.remove_entity(*it);
			}
		};

		// Delete quantities
		auto quantities = f.instances_by_type("IfcPhysicalQuantity");
        for (auto it = quantities.end() - 1; it >= quantities.begin(); --it) {
            if (!it->declaration().is("IfcPhysicalComplexQuantity")) {
                f.remove_entity(*it);
            }
        }

		// Delete complexes
		delete_reversed(f.instances_by_type("IfcPhysicalComplexQuantity"));

		auto element_quantities = f.instances_by_type("IfcElementQuantity");

		// Capture relationship nodes
		std::vector<express::entity> relationships;
		auto IfcRelDefinesByProperties = f.schema()->declaration_by_name("IfcRelDefinesByProperties");

		for (auto& eq : element_quantities) {
            auto rels = eq.file()->get_inverse(eq.id(), IfcRelDefinesByProperties, -1);
			for (auto& rel : rels) {
				relationships.push_back(rel);
			}
		}

		// Delete element quantities
		delete_reversed(element_quantities);


		// Delete relationship nodes
		for (auto& rel : relationships) {
			f.remove_entity(rel);
		}
	}

	ifcopenshell::geom::settings settings;
	settings.get<ifcopenshell::geom::settings::UseWorldCoords>().value = false;
	settings.get<ifcopenshell::geom::settings::WeldVertices>().value = false;
	settings.get<ifcopenshell::geom::settings::ReorientShells>().value = true;
	settings.get<ifcopenshell::geom::settings::ConvertBackUnits>().value = true;
	settings.get<ifcopenshell::geom::settings::IteratorOutput>().value = ifcopenshell::geom::settings::NATIVE;

	ifcopenshell::geom::iterator context_iterator(ifcopenshell::geom::kernels::construct(&f, "opencascade", settings, logger), settings, &f, {}, 1, logger);

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
	latebound_access::set(application, "ApplicationIdentifier", std::string("IfcConvert") + IFCOPENSHELL_VERSION);

	auto ownerhist = latebound_access::create(f, "IfcOwnerHistory");
	latebound_access::set(ownerhist, "OwningUser", pando);
	latebound_access::set(ownerhist, "OwningApplication", application);
	latebound_access::set(ownerhist, "ChangeAction", std::string("MODIFIED"));
	latebound_access::set(ownerhist, "CreationDate", (int64_t)time(0));

	express::base quantity;
	std::vector<express::base> objects;
	std::shared_ptr<ifcopenshell::geom::native> previous_geometry_pointer;

	for (;; ++num_created) {
		bool has_more = true;
		if (num_created) {
			has_more = context_iterator.next();
		}
		std::unique_ptr<ifcopenshell::geom::native_element> geom_object;
		if (has_more) {
			geom_object = context_iterator.get_native();
		}

		if (geom_object && geom_object->geometry_pointer() == previous_geometry_pointer) {
			// @todo
			objects.push_back(geom_object->product());
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

			std::vector<express::base> quantities;

			double a, b, c;
			if (geom_object->geometry().calculate_surface_area(a)) {
				auto quantity_area = latebound_access::create(f, "IfcQuantityArea");
				latebound_access::set(quantity_area, "Name", std::string("Total Surface Area"));
				latebound_access::set(quantity_area, "AreaValue", a);
				quantities.push_back(quantity_area);
			}

			if (geom_object->geometry().calculate_volume(a)) {
				auto quantity_volume = latebound_access::create(f, "IfcQuantityVolume");
				latebound_access::set(quantity_volume, "Name", std::string("Volume"));
				latebound_access::set(quantity_volume, "VolumeValue", a);
				quantities.push_back(quantity_volume);
			}

			if (geom_object->calculate_projected_surface_area(a, b, c)) {
				auto quantity_area = latebound_access::create(f, "IfcQuantityArea");
				latebound_access::set(quantity_area, "Name", std::string("Footprint Area"));
				latebound_access::set(quantity_area, "AreaValue", c);
				quantities.push_back(quantity_area);
			}

			auto quantity_complex = latebound_access::create(f, "IfcPhysicalComplexQuantity");
			latebound_access::set(quantity_complex, "Name", std::string("Shape Validation Properties"));
			quantities.push_back(quantity_complex);

			std::vector<express::base> quantities_2;

			for (auto& part : geom_object->geometry()) {
				auto quantity_count = latebound_access::create(f, "IfcQuantityCount");
				latebound_access::set(quantity_count, "Name", std::string("Surface Genus"));
				latebound_access::set(quantity_count, "Description", '#' + boost::lexical_cast<std::string>(part.ItemId()));
				latebound_access::set(quantity_count, "CountValue", (int64_t) part.shape()->surface_genus());

				quantities_2.push_back(quantity_count);
			}

			latebound_access::set(quantity_complex, "HasQuantities", quantities_2);

			if (!quantities.empty()) {
				quantity = latebound_access::create(f, "IfcElementQuantity");
				latebound_access::set(quantity, "OwnerHistory", ownerhist);
				latebound_access::set(quantity, "Quantities", quantities);
			}

			// @todo
			objects.push_back(geom_object->product());
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
				if (old_progress != progress) logger.progress_bar(progress);
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
		logger.status("\rDone writing quantities for " + boost::lexical_cast<std::string>(num_created) +
			" objects                                ");
	}

}
