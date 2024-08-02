#ifndef TAXONOMY_H
#define TAXONOMY_H

#include "../ifcparse/IfcBaseClass.h"
#include "../ifcparse/IfcLogger.h"

#include "ConversionSettings.h"

#include <boost/variant.hpp>
#include <boost/functional/hash.hpp>
#include <boost/math/constants/constants.hpp>

#include <Eigen/Dense>

#include <map>
#include <string>
#include <tuple>
#include <exception>
#include <numeric>

#ifndef TAXONOMY_USE_UNIQUE_PTR
#ifndef TAXONOMY_USE_NAKED_PTR
#define TAXONOMY_USE_SHARED_PTR
#endif
#endif

#ifdef TAXONOMY_USE_SHARED_PTR
#include <memory>
#endif

// @todo don't do std::less but use hashing and cache hash values.

namespace boost { inline std::size_t hash_value(const blank&) { return 0; } }

namespace ifcopenshell {

	namespace geometry {

		namespace taxonomy {

#ifdef TAXONOMY_USE_SHARED_PTR
			template <typename T>
			T clone(T& t) {
				return t;
			}
			template <typename T, typename U>
			std::shared_ptr<T> cast(const std::shared_ptr<U>& u);
			template <typename T, typename U>
			std::shared_ptr<T> dcast(const std::shared_ptr<U>& u);
#endif
#ifdef TAXONOMY_USE_UNIQUE_PTR
			// untested currently
			template <typename T>
			T clone(T& t) {
				return t->clone_();
			}
			template <typename T, typename U>
			T* cast(const std::unique_ptr<U>& u);
			template <typename T, typename U>
			T* dcast(const std::unique_ptr<U>& u);
#endif
#ifdef TAXONOMY_USE_NAKED_PTR
			// untested currently
			template <typename T>
			T clone(T& t) {
				return t->clone_();
			}
			template <typename T, typename U>
			T* cast(const U*& u);
			template <typename T, typename U>
			T* dcast(const U*& u);
#endif

#ifdef TAXONOMY_USE_SHARED_PTR
#define DECLARE_PTR(item) \
typedef std::shared_ptr<item> ptr; \
typedef std::shared_ptr<const item> const_ptr;
#endif
#ifdef TAXONOMY_USE_UNIQUE_PTR
#define DECLARE_PTR(item) \
typedef std::uniqe_ptr<item> ptr; \
typedef std::uniqe_ptr<const item> ptr;
#endif
#ifdef TAXONOMY_USE_NAKED_PTR
#define DECLARE_PTR(item) \
typedef item* ptr; \
typedef item const* ptr;
#endif

			class topology_error : public std::runtime_error {
			public:
				topology_error() : std::runtime_error("Generic topology error") {}
				topology_error(const char* const s) : std::runtime_error(s) {}
			};

			enum kinds { MATRIX4, POINT3, DIRECTION3, LINE, CIRCLE, ELLIPSE, BSPLINE_CURVE, OFFSET_CURVE, PLANE, CYLINDER, SPHERE, TORUS, BSPLINE_SURFACE, EDGE, LOOP, FACE, SHELL, SOLID, LOFT, EXTRUSION, REVOLVE, SWEEP_ALONG_CURVE, NODE, COLLECTION, BOOLEAN_RESULT, PIECEWISE_FUNCTION, COLOUR, STYLE };

			const std::string& kind_to_string(kinds k);

			struct item {
			private:
				uint32_t identity_;
				static std::atomic_uint32_t counter_;
				mutable size_t computed_hash_;
			public:
				DECLARE_PTR(item)

				const IfcUtil::IfcBaseInterface* instance;

				boost::optional<bool> orientation;

				virtual item* clone_() const = 0;
				virtual kinds kind() const = 0;
				virtual void print(std::ostream&, int indent = 0) const;
				virtual void reverse() { throw taxonomy::topology_error(); }
				virtual size_t calc_hash() const = 0;
				virtual size_t hash() const {
					if (computed_hash_) {
						return computed_hash_;
					}
					computed_hash_ = calc_hash();
					if (computed_hash_ == 0) {
						computed_hash_++;
					}
					return computed_hash_;
				}

				item(const IfcUtil::IfcBaseInterface* instance = nullptr) : identity_(counter_++), computed_hash_(0), instance(instance) {}

				virtual ~item() {}

				uint32_t identity() const { return identity_; }
			};

			namespace {

				template <typename T>
				const T& eigen_defaults();

				template <>
				const Eigen::Vector3d& eigen_defaults<Eigen::Vector3d>() {
					static Eigen::Vector3d identity = Eigen::Vector3d::Zero();
					return identity;
				}

				template <>
				const Eigen::Matrix4d& eigen_defaults<Eigen::Matrix4d>() {
					static Eigen::Matrix4d identity = Eigen::Matrix4d::Identity();
					return identity;
				}

			}

			template <typename T>
			struct eigen_base {
				T* components_;

				eigen_base() {
					components_ = nullptr;
				}

				eigen_base(const eigen_base& other) {
					this->components_ = other.components_ ? new T(*other.components_) : nullptr;
				}

				eigen_base(const T& other) {
					this->components_ = new T(other);
				}

				eigen_base& operator=(const eigen_base& other) {
					if (this != &other) {
						this->components_ = other.components_ ? new T(*other.components_) : nullptr;
					}
					return *this;
				}

				void print_impl(std::ostream& o, const std::string& class_name, int indent = 0) const {
					o << std::string(indent, ' ') << class_name;
					if (this->components_) {
						int n = T::RowsAtCompileTime * T::ColsAtCompileTime;
						for (int i = 0; i < n; ++i) {
							o << " " << (*components_)(i);
						}
					}
					o << std::endl;
				}

				virtual ~eigen_base() {
					delete this->components_;
				}

				const T& ccomponents() const {
					if (this->components_) {
						return *this->components_;
					} else {
						return eigen_defaults<T>();
					}
				}

				T& components() {
					if (!this->components_) {
						this->components_ = new T(eigen_defaults<T>());
					}
					return *this->components_;
				}

				explicit operator bool() const {
					return components_;
				}

				uint32_t hash_components() const {
					size_t h = std::hash<size_t>{}(T::RowsAtCompileTime);
					boost::hash_combine(h, std::hash<size_t>{}(T::ColsAtCompileTime));
					if (components_) {
						for (int i = 0; i < components_->size(); ++i) {
							auto elem = *(components_->data() + (size_t)i);
							boost::hash_combine(h, std::hash<typename T::Scalar>()(elem));
						}
					}
					return (uint32_t)h;
				}
			};

			struct matrix4 : public item, public eigen_base<Eigen::Matrix4d> {
			private:
				void init(const Eigen::Vector3d& o, const Eigen::Vector3d& z, const Eigen::Vector3d& x) {
					auto X = x.normalized();
					auto Y = z.cross(x).normalized();
					auto Z = z.normalized();
					components_ = new Eigen::Matrix4d;
					(*components_) <<
						X(0), Y(0), Z(0), o(0),
						X(1), Y(1), Z(1), o(1),
						X(2), Y(2), Z(2), o(2),
						0, 0, 0, 1.;
					if (is_identity()) {
						// @todo detect this earlier to save us the heapalloc.
						delete components_;
						components_ = nullptr;
						tag = IDENTITY;
					}
				}
			public:
				DECLARE_PTR(matrix4)

				enum tag_t {
					IDENTITY, AFFINE_WO_SCALE, AFFINE_W_UNIFORM_SCALE, AFFINE_W_NONUNIFORM_SCALE, OTHER
				};
				tag_t tag;

				matrix4() : eigen_base(), tag(IDENTITY) {}
				matrix4(const Eigen::Matrix4d& c) : eigen_base(c), tag(OTHER) {}
				matrix4(const Eigen::Vector3d& o, const Eigen::Vector3d& z, const Eigen::Vector3d& x) : tag(AFFINE_WO_SCALE) {
					init(o, z, x);
				}
				matrix4(const Eigen::Vector3d& o, const Eigen::Vector3d& z) : tag(AFFINE_WO_SCALE) {
					auto x = Eigen::Vector3d(1, 0, 0);
					auto y = z.cross(x);
					if (y.squaredNorm() < 1.e-7) {
						x = Eigen::Vector3d(0, 0, 1);
					}
					init(o, z, x);
				}

				bool is_identity() const {
					return !components_ || components_->isIdentity();
				}

				void print(std::ostream& o, int indent = 0) const;

				virtual matrix4* clone_() const { return new matrix4(*this); }
				virtual kinds kind() const { return MATRIX4; }

				virtual size_t calc_hash() const {
					auto v = std::make_tuple(static_cast<size_t>(MATRIX4), hash_components());
					return boost::hash<decltype(v)>{}(v);
				}

				Eigen::Vector3d translation_part() const { return ccomponents().col(3).head<3>(); }
			};

			struct colour : public item, public eigen_base<Eigen::Vector3d> {
				DECLARE_PTR(colour)

				void print(std::ostream& o, int indent = 0) const;

				virtual colour* clone_() const { return new colour(*this); }
				virtual kinds kind() const { return COLOUR; }

				virtual size_t calc_hash() const {
					auto v = std::make_tuple(static_cast<size_t>(COLOUR), hash_components());
					return boost::hash<decltype(v)>{}(v);
				}

				colour() : eigen_base() {}
				colour(double r, double g, double b) { components() << r, g, b; }

				const double& r() const { return ccomponents()[0]; }
				const double& g() const { return ccomponents()[1]; }
				const double& b() const { return ccomponents()[2]; }
			};

			struct style : public item {
				DECLARE_PTR(style)

				std::string name;
				colour diffuse;
				colour specular;
				double specularity, transparency;

				void print(std::ostream& o, int indent = 0) const;

				virtual style* clone_() const { return new style(*this); }
				virtual kinds kind() const { return STYLE; }

				virtual size_t calc_hash() const {
					auto v = std::make_tuple(static_cast<size_t>(STYLE), name, diffuse.hash(), specular.hash(), specularity, transparency);
					return boost::hash<decltype(v)>{}(v);
				}

				// @todo equality implementation based on values?
				bool operator==(const style& other) const { return instance == other.instance; }

				style() : specularity(std::numeric_limits<double>::quiet_NaN()), transparency(std::numeric_limits<double>::quiet_NaN()) {}
				style(const std::string& name) : name(name), specularity(std::numeric_limits<double>::quiet_NaN()), transparency(std::numeric_limits<double>::quiet_NaN()) {}

				bool has_specularity() const {
					return !std::isnan(specularity);
				}

				bool has_transparency() const {
					return !std::isnan(transparency);
				}
			};

			struct geom_item : public item {
				DECLARE_PTR(geom_item)

				style::ptr surface_style;
				matrix4::ptr matrix;

				geom_item(const IfcUtil::IfcBaseInterface* instance = nullptr) : item(instance), surface_style(nullptr) {}
				geom_item(const IfcUtil::IfcBaseInterface* instance, matrix4::ptr m) : item(instance), surface_style(nullptr), matrix(m) {}
				geom_item(matrix4::ptr m) : surface_style(nullptr), matrix(m) {}
			};

			struct implicit_item : public geom_item {
				DECLARE_PTR(implicit_item)
				using geom_item::geom_item;

				virtual item::ptr evaluate() const = 0;
			};

			struct piecewise_function_impl; // forward declaration
			struct piecewise_function : public implicit_item {
            DECLARE_PTR(piecewise_function)

				using spans_t = std::vector<std::pair<double, std::function<Eigen::Matrix4d(double u)>>>;

            piecewise_function(double start, const spans_t& s, ifcopenshell::geometry::Settings* settings = nullptr, const IfcUtil::IfcBaseInterface* instance = nullptr);
            piecewise_function(double start, const std::vector<piecewise_function::ptr>& pwfs, ifcopenshell::geometry::Settings* settings = nullptr, const IfcUtil::IfcBaseInterface* instance = nullptr);
            piecewise_function(piecewise_function&&) = default;
            piecewise_function(const piecewise_function&);
            virtual ~piecewise_function();

				const ifcopenshell::geometry::Settings* settings_ = nullptr;

				const spans_t& spans() const;
				bool is_empty() const;
				double start() const;
				double end() const;
				double length() const;

				virtual piecewise_function* clone_() const { return new piecewise_function(*this); }
				virtual kinds kind() const { return PIECEWISE_FUNCTION; }

				virtual size_t calc_hash() const	{
					auto v = std::make_tuple(static_cast<size_t>(PIECEWISE_FUNCTION), 0);
					return boost::hash<decltype(v)>{}(v);
				}

				/// @brief returns a vector of "distance along" points where the evaluate function computes loop points
				std::vector<double> evaluation_points() const;

				/// @brief returns a vector of "distance along" points between ustart and uend
            /// @param ustart starting location
            /// @param uend ending location
            /// @param nsteps number of steps to evaluate
            std::vector<double> evaluation_points(double ustart, double uend, unsigned nsteps) const;

            /// @brief evaluates the piecewise function between start and end
				/// evaluation point step size is taken from the settings object
            item::ptr evaluate() const override;

            /// @brief evaluates the piecewise function between ustart and uend
				/// if ustart and uend are out of range, the range of values evaluated
				/// are constrained to start_ and start_+length_
            /// @param ustart starting location
            /// @param uend ending location
            /// @param nsteps number of steps to evaluate
            /// @return taxonomy::loop::ptr
            item::ptr evaluate(double ustart, double uend, unsigned nsteps) const;

				/// @brief evaluates the piecewise function at u
				/// @param u u is constrained to be between start_ and start_+length
				/// @return 4x4 placement matrix
				Eigen::Matrix4d evaluate(double u) const;

            private:
				    // note: it would be better if this were a std::unique_ptr, but that requires having the full definition
					 // of piecewise_function_impl in this header file, which defeats the purpose of the PIMPL idiom.
					 // if this is a std::unique_ptr, then the _ifcopenshell_wrapper library doesn't compile
                piecewise_function_impl* impl_ = nullptr;
			};

#ifdef TAXONOMY_USE_SHARED_PTR
			typedef std::shared_ptr<item> ptr;
			typedef std::shared_ptr<const item> const_ptr;
			template<typename T, typename... Args>
			std::shared_ptr<T> make(Args&&... args) {
				return std::make_shared<T>(std::forward<Args>(args)...);
			}
#endif
#ifdef TAXONOMY_USE_UNIQUE_PTR
			typedef std::uniqe_ptr<item> ptr;
			typedef std::uniqe_ptr<const item> ptr;
			template<typename T, typename... Args>
			std::uniqe_ptr<T> make(Args&&... args) {
				return new T(std::forward<Args>(args)...));
			}
#endif
#ifdef TAXONOMY_USE_NAKED_PTR
			typedef item* ptr;
			typedef item const* ptr;
			template<typename T, typename... Args>
			T* make(Args&&... args) {
				return new T(std::forward<Args>(args)...));
			}
#endif

			bool less(item::const_ptr, item::const_ptr);

			struct less_functor {
				bool operator()(item::const_ptr a, item::const_ptr b) const {
					return less(a, b);
				}
			};

			// @todo make 4d for easier multiplication
			template <size_t N>
			struct cartesian_base : public item, public eigen_base<Eigen::Vector3d> {
				cartesian_base() : eigen_base() {}
				cartesian_base(const Eigen::Vector3d& c) : eigen_base(c) {}
				cartesian_base(double x, double y, double z = 0.) : eigen_base(Eigen::Vector3d(x, y, z)) {}
			};

			struct point3 : public cartesian_base<3> {
				DECLARE_PTR(point3)

				virtual point3* clone_() const { return new point3(*this); }
				virtual kinds kind() const { return POINT3; }

				virtual size_t calc_hash() const {
					auto v = std::make_tuple(static_cast<size_t>(POINT3), hash_components());
					return boost::hash<decltype(v)>{}(v);
				}

				void print(std::ostream& o, int indent = 0) const;

				point3() : cartesian_base() {}
				point3(const Eigen::Vector3d& c) : cartesian_base(c) {}
				point3(double x, double y, double z = 0.) : cartesian_base(x, y, z) {}
			};

			struct direction3 : public cartesian_base<3> {
				DECLARE_PTR(direction3)

				virtual direction3* clone_() const { return new direction3(*this); }
				virtual kinds kind() const { return DIRECTION3; }

				virtual size_t calc_hash() const {
					auto v = std::make_tuple(static_cast<size_t>(DIRECTION3), hash_components());
					return boost::hash<decltype(v)>{}(v);
				}

				void print(std::ostream& o, int indent = 0) const;

				direction3() : cartesian_base() {}
				direction3(const Eigen::Vector3d& c) : cartesian_base(c) {}
				direction3(double x, double y, double z = 0.) : cartesian_base(x, y, z) {}
			};

			struct curve : public geom_item {
				void print_impl(std::ostream& o, const std::string& classname, int indent = 0) const {
					o << std::string(indent, ' ') << classname << std::endl;
					this->matrix->print(o, indent + 4);
				}
			};

			struct line : public curve {
				DECLARE_PTR(line)

				virtual line* clone_() const { return new line(*this); }
				virtual kinds kind() const { return LINE; }

				virtual size_t calc_hash() const {
					auto v = std::make_tuple(static_cast<size_t>(LINE), matrix->hash_components());
					return boost::hash<decltype(v)>{}(v);
				}

				void print(std::ostream& o, int indent = 0) const;
			};

			struct circle : public curve {
				DECLARE_PTR(circle)

				double radius;

				virtual circle* clone_() const { return new circle(*this); }
				virtual kinds kind() const { return CIRCLE; }

				virtual size_t calc_hash() const {
					auto v = std::make_tuple(static_cast<size_t>(CIRCLE), matrix->hash_components(), radius);
					return boost::hash<decltype(v)>{}(v);
				}

				void print(std::ostream& o, int indent = 0) const;

				static circle::ptr from_3_points(const Eigen::Vector3d& p1, const Eigen::Vector3d& p2, const Eigen::Vector3d& p3) {
					Eigen::Vector3d t = p2 - p1;
					Eigen::Vector3d u = p3 - p1;
					Eigen::Vector3d v = p3 - p2;

					auto norm = t.cross(u);
					auto mag = norm.dot(norm);

					auto iwsl2 = 1. / (2. * mag);
					auto tt = t.dot(t);
					auto uu = u.dot(u);

					auto orig = p1 + (u * tt * u.dot(v) - t * uu * t.dot(v)) * iwsl2;

					if (!orig.array().isNaN().any()) {
						auto radius = std::sqrt(tt * uu * v.dot(v) * iwsl2 * 0.5f);
						auto ax = norm / std::sqrt(mag);


						auto c = make<circle>();
						c->radius = radius;
						c->matrix = taxonomy::make<taxonomy::matrix4>(orig, ax);
						return c;
					}

					return nullptr;
				}
			};

			struct ellipse : public curve {
				DECLARE_PTR(ellipse)

				double radius;
				double radius2;

				virtual ellipse* clone_() const { return new ellipse(*this); }
				virtual kinds kind() const { return ELLIPSE; }

				virtual size_t calc_hash() const {
					auto v = std::make_tuple(static_cast<size_t>(ELLIPSE), matrix->hash_components(), radius, radius2);
					return boost::hash<decltype(v)>{}(v);
				}

				void print(std::ostream& o, int indent = 0) const;
			};

			struct bspline_curve : public curve {
				DECLARE_PTR(bspline_curve)

				virtual bspline_curve* clone_() const { return new bspline_curve(*this); }
				virtual kinds kind() const { return BSPLINE_CURVE; }

				virtual size_t calc_hash() const {
					size_t h = std::hash<size_t>{}(BSPLINE_CURVE);
					for (auto& x : control_points) {
						boost::hash_combine(h, x->hash());
					}
					for (auto& x : multiplicities) {
						boost::hash_combine(h, std::hash<int>{}(x));
					}
					for (auto& x : knots) {
						boost::hash_combine(h, std::hash<double>{}(x));
					}
					if (weights) {
						for (auto& x : *weights) {
							boost::hash_combine(h, std::hash<double>{}(x));
						}
					}
					boost::hash_combine(h, std::hash<int>{}(degree));
					return h;
				}

				std::vector<point3::ptr> control_points;
				std::vector<int> multiplicities;
				std::vector<double> knots;
				boost::optional<std::vector<double>> weights;
				int degree;
			};

			struct offset_curve : public curve {
				DECLARE_PTR(offset_curve)

				direction3::ptr reference;
				double offset;
				item::ptr basis;

				virtual offset_curve* clone_() const { return new offset_curve(*this); }
				virtual kinds kind() const { return OFFSET_CURVE; }

				virtual size_t calc_hash() const {
					auto v = std::make_tuple(static_cast<size_t>(OFFSET_CURVE), reference->hash(), offset, basis ? basis->hash() : size_t(0));
					return boost::hash<decltype(v)>{}(v);
				}
			};

			struct trimmed_curve : public geom_item {
				DECLARE_PTR(trimmed_curve)

				// @todo The copy constructor of point3 within the variant fails on the avx instruction
				// on the default gcc in Ubuntu 18.04 and a recent AMD Ryzen. Probably due to allignment.
				boost::variant<boost::blank, point3::ptr, double> start, end;

				// @todo somehow account for the fact that curve in IFC can be trimmed curve, polyline and composite curve as well.
				item::ptr basis;

				// @todo does this make sense? this is to accommodate for the fact that orientation is defined on both TrimmedCurve as well CompCurveSegment
				boost::optional<bool> curve_sense;

				trimmed_curve() : basis(nullptr) {}
				trimmed_curve(const point3::ptr& a, const point3::ptr& b) : start(a), end(b), basis(nullptr) {}

				virtual void reverse() {
					// std::swap(start, end);
					orientation = !orientation.get_value_or(true);
				}

				void print(std::ostream& o, int indent = 0) const;
			};

			struct edge : public trimmed_curve {
				DECLARE_PTR(edge)

				edge() : trimmed_curve() {}
				edge(const point3::ptr& a, const point3::ptr& b) : trimmed_curve(a, b) {}

				// @todo how to express similarity between trimmed_curve and edge?
				virtual edge* clone_() const { return new edge(*this); }
				virtual kinds kind() const { return EDGE; }

				virtual size_t calc_hash() const {
					auto v = std::make_tuple(static_cast<size_t>(EDGE), start, end, basis ? basis->hash() : size_t(0), curve_sense ? *curve_sense ? 2 : 1 : 0);
					return boost::hash<decltype(v)>{}(v);
				}
			};

			template <typename T = item>
			struct collection_base : public geom_item {
				std::vector<typename T::ptr> children;

				collection_base() {}
				collection_base(const collection_base& other)
					: geom_item()
				{
					std::transform(other.children.begin(), other.children.end(), std::back_inserter(children), [](typename T::ptr p) { return clone(p); });
				}

				/*
				template <typename T>
				std::vector<typename T::ptr> children_as() const {
					std::vector<typename T::ptr> ts;
					ts.reserve(children.size());
					std::for_each(children.begin(), children.end(), [&ts](ptr i){
						auto v = dcast<T>(i);
						if (v) {
							ts.push_back(v);
						}
					});
					return ts;
				}
				*/

				virtual void reverse() {
					// @todo this needs to create copies of the children in case of shared_ptr
					std::reverse(children.begin(), children.end());
					for (auto& child : children) {
						child->reverse();
					}
				}

				virtual void print_impl(std::ostream&, int) const {
					// empty on purpose
				}

				void print(std::ostream& o, int indent = 0) const {
					o << std::string(indent, ' ') << kind_to_string(kind()) << std::endl;
					if (matrix && !matrix->is_identity()) {
						matrix->print(o, indent + 4);
					}
					for (auto& c : children) {
						c->print(o, indent + 4);
					}
					print_impl(o, indent + 4);
				}

				virtual ~collection_base() {
#ifdef TAXONOMY_USE_NAKED_PTR
					for (auto& c : children) {
						delete c;
					}
#endif
				}

				uint32_t hash_elements() const {
					size_t h = 0;
					for (auto& c : children) {
						boost::hash_combine(h, c->hash());
					}
					// @todo should we really use uint32_t instead of size_t for hashes?
					return (uint32_t) h;
				}
			};

			struct collection : public collection_base<geom_item> {
				DECLARE_PTR(collection)

				virtual collection* clone_() const { return new collection(*this); }
				virtual kinds kind() const { return COLLECTION; }

				virtual size_t calc_hash() const {
					auto v = std::make_tuple(static_cast<size_t>(COLLECTION), hash_elements());
					return boost::hash<decltype(v)>{}(v);
				}
			};


			struct loop : public collection_base<edge> {
				DECLARE_PTR(loop)

				boost::optional<bool> external, closed;
				boost::optional<taxonomy::piecewise_function::ptr> pwf;

				bool is_polyhedron() const {
					for (auto& e : children) {
						if (e->basis != nullptr) {
							if (e->basis->kind() != LINE) {
								return false;
							}
						}
					}
					return true;
				}

				void calculate_linear_edge_curves() const {
					for (auto& e : children) {
						if (e->basis == nullptr) {
							if (e->start.which() == 1 && e->end.which() == 1) {
								auto ln = make<taxonomy::line>();
								auto a = boost::get<point3::ptr>(e->start)->ccomponents();
								auto b = boost::get<point3::ptr>(e->end)->ccomponents();
								ln->matrix = make<matrix4>(a, b - a);
								e->basis = ln;
							}
						}
					}
				}

				void remove_linear_edge_curves() const {
					for (auto& e : children) {
						if (e->basis != nullptr && e->basis->kind() == LINE) {
							e->basis = nullptr;
						}
					}
				}

				virtual loop* clone_() const { return new loop(*this); }
				virtual kinds kind() const { return LOOP; }

				virtual size_t calc_hash() const {
					auto v = std::make_tuple(static_cast<size_t>(LOOP), hash_elements(), external ? *external ? 2 : 1 : 0, closed ? *closed ? 2 : 1 : 0);
					return boost::hash<decltype(v)>{}(v);
				}
			};

			struct face : public collection_base<loop> {
				DECLARE_PTR(face)

				item::ptr basis;

				virtual face* clone_() const { return new face(*this); }
				virtual kinds kind() const { return FACE; }

				virtual void print_impl(std::ostream& o, int indent) const {
					if (basis) {
						o << std::string(indent, ' ') << "basis" << std::endl;
						basis->print(o, indent + 4);
					}
				}

				virtual size_t calc_hash() const {
					auto v = std::make_tuple(static_cast<size_t>(FACE), hash_elements(), basis ? basis->hash() : size_t(0));
					return boost::hash<decltype(v)>{}(v);
				}
			};

			struct shell : public collection_base<face> {
				DECLARE_PTR(shell)

				boost::optional<bool> closed;

				virtual void print_impl(std::ostream& o, int indent) const {
					using namespace std::string_literals;
					o << std::string(indent, ' ') << "closed " << (closed ? *closed ? "yes"s : "no"s : "unknown"s) << std::endl;
				}

				virtual shell* clone_() const { return new shell(*this); }
				virtual kinds kind() const { return SHELL; }

				virtual size_t calc_hash() const {
					auto v = std::make_tuple(static_cast<size_t>(SHELL), hash_elements(), closed ? *closed ? 2 : 1 : 0);
					return boost::hash<decltype(v)>{}(v);
				}
			};

			struct solid : public collection_base<shell> {
				DECLARE_PTR(solid)

				virtual solid* clone_() const { return new solid(*this); }
				virtual kinds kind() const { return SOLID; }

				virtual size_t calc_hash() const {
					auto v = std::make_tuple(static_cast<size_t>(SOLID), hash_elements());
					return boost::hash<decltype(v)>{}(v);
				}
			};

			struct loft : public collection_base<face> {
				DECLARE_PTR(loft)

				item::ptr axis;

				virtual loft* clone_() const { return new loft(*this); }
				virtual kinds kind() const { return LOFT; }

				virtual void print_impl(std::ostream& o, int indent) const {
					o << std::string(indent, ' ') << "axis" << std::endl;
					axis->print(o, indent + 4);
				}

				virtual size_t calc_hash() const {
					auto v = std::make_tuple(static_cast<size_t>(LOFT), hash_elements(), axis ? axis->hash() : size_t(0));
					return boost::hash<decltype(v)>{}(v);
				}
			};

			struct surface : public geom_item {};

			struct plane : public surface {
				DECLARE_PTR(plane)

				virtual plane* clone_() const { return new plane(*this); }
				virtual kinds kind() const { return PLANE; }

				virtual size_t calc_hash() const {
					auto v = std::make_tuple(static_cast<size_t>(PLANE), matrix->hash_components());
					return boost::hash<decltype(v)>{}(v);
				}
			};

			struct cylinder : public surface {
				DECLARE_PTR(cylinder)

				double radius;

				virtual cylinder* clone_() const { return new cylinder(*this); }
				virtual kinds kind() const { return CYLINDER; }

				virtual size_t calc_hash() const {
					auto v = std::make_tuple(static_cast<size_t>(CYLINDER), matrix->hash_components());
					return boost::hash<decltype(v)>{}(v);
				}
			};

			struct sphere : public surface {
				DECLARE_PTR(sphere)

				double radius;

				virtual sphere* clone_() const { return new sphere(*this); }
				virtual kinds kind() const { return SPHERE; }

				virtual size_t calc_hash() const {
					auto v = std::make_tuple(static_cast<size_t>(SPHERE), matrix->hash_components());
					return boost::hash<decltype(v)>{}(v);
				}
			};

			struct torus : public surface {
				DECLARE_PTR(torus)

				double radius1;
				double radius2;

				virtual torus* clone_() const { return new torus(*this); }
				virtual kinds kind() const { return TORUS; }

				virtual size_t calc_hash() const {
					auto v = std::make_tuple(static_cast<size_t>(TORUS), matrix->hash_components());
					return boost::hash<decltype(v)>{}(v);
				}
			};

			struct bspline_surface : public surface {
				DECLARE_PTR(bspline_surface)

				virtual bspline_surface* clone_() const { return new bspline_surface(*this); }
				virtual kinds kind() const { return BSPLINE_SURFACE; }

				virtual size_t calc_hash() const {
					size_t h = std::hash<size_t>{}(BSPLINE_SURFACE);
					boost::hash_combine(h, std::hash<size_t>{}(control_points.size()));
					for (auto& xs : control_points) {
						for (auto& x : xs) {
							boost::hash_combine(h, x->hash());
						}
					}
					for (auto& xs : multiplicities) {
						for (auto& x : xs) {
							boost::hash_combine(h, std::hash<int>{}(x));
						}
					}
					for (auto& xs : knots) {
						for (auto& x : xs) {
							boost::hash_combine(h, std::hash<double>{}(x));
						}
					}
					if (weights) {
						for (auto& xs : *weights) {
							for (auto& x : xs) {
								boost::hash_combine(h, std::hash<double>{}(x));
							}
						}
					}
					boost::hash_combine(h, std::hash<int>{}(degree[0]));
					boost::hash_combine(h, std::hash<int>{}(degree[1]));
					return h;
				}

				std::vector<std::vector<point3::ptr>> control_points;
				std::array<std::vector<int>, 2> multiplicities;
				std::array<std::vector<double>, 2> knots;
				boost::optional<std::vector<std::vector<double>>> weights;
				std::array<int, 2> degree;
			};

			struct sweep : public geom_item {
				DECLARE_PTR(sweep)

				item::ptr basis;

				sweep(face::ptr b) : basis(b) {}
				sweep(matrix4::ptr m, item::ptr b) : geom_item(m), basis(b) {}
			};

			struct extrusion : public sweep {
				DECLARE_PTR(extrusion)

				direction3::ptr direction;
				double depth;

				virtual extrusion* clone_() const { return new extrusion(*this); }
				virtual kinds kind() const { return EXTRUSION; }

				extrusion(matrix4::ptr m, item::ptr basis, direction3::ptr dir, double d) : sweep(m, basis), direction(dir), depth(d) {}

				void print(std::ostream& o, int indent = 0) const;

				virtual size_t calc_hash() const {
					auto v = std::make_tuple(static_cast<size_t>(EXTRUSION), matrix->hash_components(), basis->calc_hash(), direction->hash_components(), depth);
					return boost::hash<decltype(v)>{}(v);
				}
			};

			struct revolve : public sweep {
				DECLARE_PTR(revolve)

				point3::ptr axis_origin;
				direction3::ptr direction;
				boost::optional<double> angle;

				virtual revolve* clone_() const { return new revolve(*this); }
				virtual kinds kind() const { return REVOLVE; }

				revolve(matrix4::ptr m, item::ptr basis, point3::ptr pnt, direction3::ptr dir, const boost::optional<double>& a) : sweep(m, basis), axis_origin(pnt), direction(dir), angle(a) {}

				virtual size_t calc_hash() const {
					auto v = std::make_tuple(static_cast<size_t>(REVOLVE), matrix->hash_components(), basis->calc_hash(), axis_origin->hash_components(), direction->hash_components(), angle ? *angle : 1000.);
					return boost::hash<decltype(v)>{}(v);
				}
			};

			struct sweep_along_curve : public sweep {
				DECLARE_PTR(sweep_along_curve)

				item::ptr surface;
				item::ptr curve;

				virtual sweep_along_curve* clone_() const { return new sweep_along_curve(*this); }
				virtual kinds kind() const { return SWEEP_ALONG_CURVE; }

				sweep_along_curve(matrix4::ptr m, face::ptr basis, item::ptr surf, item::ptr crv) : sweep(m, basis), surface(surf), curve(crv) {}

				virtual size_t calc_hash() const {
					auto v = std::make_tuple(static_cast<size_t>(SWEEP_ALONG_CURVE), matrix->hash_components(), basis->calc_hash(), surface->calc_hash(), curve->calc_hash());
					return boost::hash<decltype(v)>{}(v);
				}
			};

			struct node : public item {
				DECLARE_PTR(node)

				// std::map<std::string, geom_item> representations;

				virtual node* clone_() const { return new node(*this); }
				virtual kinds kind() const { return NODE; }

				void print(std::ostream&, int = 0) const {}

				virtual size_t calc_hash() const {
					auto v = std::make_tuple(static_cast<size_t>(NODE));
					return boost::hash<decltype(v)>{}(v);
				}
			};

			struct boolean_result : public collection_base<geom_item> {
				DECLARE_PTR(boolean_result)

				enum operation_t {
					UNION, SUBTRACTION, INTERSECTION
				};

				virtual boolean_result* clone_() const { return new boolean_result(*this); }
				virtual kinds kind() const { return BOOLEAN_RESULT; }
				operation_t operation;

				static const std::string& operation_str(operation_t op) {
					using namespace std::string_literals;
					static std::string s[] = { "union"s, "subtraction"s, "intersection"s };
					return s[(size_t)op];
				}

				virtual size_t calc_hash() const {
					auto v = std::make_tuple(static_cast<size_t>(BOOLEAN_RESULT), hash_elements(), static_cast<size_t>(operation));
					return boost::hash<decltype(v)>{}(v);
				}
			};

			namespace impl {
				typedef std::tuple<matrix4, point3, direction3, line, circle, ellipse, bspline_curve, offset_curve, plane, cylinder, sphere, torus, bspline_surface, edge, loop, face, shell, solid, loft, extrusion, revolve, sweep_along_curve, node, collection, boolean_result, piecewise_function> KindsTuple;
				typedef std::tuple<line, circle, ellipse, bspline_curve, offset_curve, loop, edge> CurvesTuple;
				typedef std::tuple<plane, cylinder, sphere, torus, bspline_surface, extrusion, revolve> SurfacesTuple;
			}

			struct type_by_kind {
				template <std::size_t N>
				using type = typename std::tuple_element<N, impl::KindsTuple>::type;

				static const size_t max = std::tuple_size<impl::KindsTuple>::value;
			};

			struct curves {
				template <std::size_t N>
				using type = typename std::tuple_element<N, impl::CurvesTuple>::type;

				static const size_t max = std::tuple_size<impl::CurvesTuple>::value;
			};

			struct surfaces {
				template <std::size_t N>
				using type = typename std::tuple_element<N, impl::SurfacesTuple>::type;

				static const size_t max = std::tuple_size<impl::SurfacesTuple>::value;
			};

			template <typename T>
			class loop_to_face_upgrade {
			private:
				boost::optional<taxonomy::face::ptr> face_;
			public:
				loop_to_face_upgrade(taxonomy::ptr item) {
					if constexpr (std::is_same_v<T, face>) {
						auto loop = taxonomy::dcast<taxonomy::loop>(item);
						if (loop) {
							loop->external = true;

							face_ = taxonomy::make<taxonomy::face>();
							(*face_)->instance = loop->instance;
							(*face_)->matrix = loop->matrix;
							(*face_)->children = { taxonomy::clone(loop) };
						}
					}
				}

				operator bool() const {
					return face_.is_initialized();
				}

				operator typename T::ptr() const {
					if constexpr (std::is_same_v<T, face>) {
						if (face_) {
							return *face_;
						}
					}
					return nullptr;
				}
			};

			template <typename T>
			class curve_to_edge_upgrade {
			private:
				boost::optional<taxonomy::edge::ptr> edge_;
			public:
				curve_to_edge_upgrade(taxonomy::ptr item) {
					if constexpr (std::is_same_v<T, edge>) {
						auto circle = taxonomy::dcast<taxonomy::circle>(item);
						auto ellipse = taxonomy::dcast<taxonomy::ellipse>(item);
						auto line = taxonomy::dcast<taxonomy::line>(item);
						auto bspline_curve = taxonomy::dcast<taxonomy::bspline_curve>(item);
						if (circle || ellipse || line || bspline_curve) {
							edge_ = taxonomy::make<taxonomy::edge>();
							if (circle) {
								(*edge_)->basis = circle;
							} else if (ellipse) {
								(*edge_)->basis = ellipse;
							} else if (line) {
								(*edge_)->basis = line;
							} else if (bspline_curve) {
								(*edge_)->basis = bspline_curve;
							}

							if (circle || ellipse) {
								// @todo
								(*edge_)->start = 0.;
								(*edge_)->end = 2 * boost::math::constants::pi<double>();
							}
						}
					}
				}

				operator bool() const {
					return edge_.is_initialized();
				}

				operator typename T::ptr() const {
					if constexpr (std::is_same_v<T, edge>) {
						if (edge_) {
							return *edge_;
						}
					}
					return nullptr;
				}
			};


			template <typename T>
			class curve_to_loop_upgrade {
			private:
				boost::optional<taxonomy::loop::ptr> loop_;
			public:
				curve_to_loop_upgrade(taxonomy::ptr item) {
					if constexpr (std::is_same_v<T, loop>) {
						auto circle = taxonomy::dcast<taxonomy::circle>(item);
						auto ellipse = taxonomy::dcast<taxonomy::ellipse>(item);
						auto line = taxonomy::dcast<taxonomy::line>(item);
						auto bspline_curve = taxonomy::dcast<taxonomy::bspline_curve>(item);
						if (circle || ellipse || line || bspline_curve) {
							auto edge = taxonomy::make<taxonomy::edge>();
							if (circle) {
								edge->basis = circle;
							} else if (ellipse) {
								edge->basis = ellipse;
							} else if (line) {
								edge->basis = line;
							} else if (bspline_curve) {
								edge->basis = bspline_curve;
							}

							if (circle || ellipse) {
								// @todo
								edge->start = 0.;
								edge->end = 2 * boost::math::constants::pi<double>();
							}

							loop_ = taxonomy::make<taxonomy::loop>();
							(*loop_)->children.push_back(edge);
						}
					}
				}

				operator bool() const {
					return loop_.is_initialized();
				}

				operator typename T::ptr() const {
					if constexpr (std::is_same_v<T, loop>) {
						if (loop_) {
							return *loop_;
						}
					}
					return nullptr;
				}
			};

			template <typename T>
			class edge_to_loop_upgrade {
			private:
				boost::optional<taxonomy::loop::ptr> loop_;
			public:
				edge_to_loop_upgrade(taxonomy::ptr item) {
					if constexpr (std::is_same_v<T, loop>) {
						auto edge = taxonomy::dcast<taxonomy::edge>(item);
						if (edge) {
							loop_ = taxonomy::make<taxonomy::loop>();
							(*loop_)->children.push_back(edge);
						}
					}
				}

				operator bool() const {
					return loop_.is_initialized();
				}

				operator typename T::ptr() const {
					if constexpr (std::is_same_v<T, loop>) {
						if (loop_) {
							return *loop_;
						}
					}
					return nullptr;
				}
			};


			template <typename T>
			class curve_to_face_upgrade {
			private:
				boost::optional<taxonomy::face::ptr> face_;
			public:
				curve_to_face_upgrade(taxonomy::ptr item) {
					if constexpr (std::is_same_v<T, edge>) {
						auto circle = taxonomy::dcast<taxonomy::circle>(item);
						auto ellipse = taxonomy::dcast<taxonomy::ellipse>(item);
						auto line = taxonomy::dcast<taxonomy::line>(item);
						auto bspline_curve = taxonomy::dcast<taxonomy::bspline_curve>(item);
						if (circle || ellipse || line || bspline_curve) {
							auto edge = taxonomy::make<taxonomy::edge>();
							if (circle) {
								edge->basis = circle;
							} else if (ellipse) {
								edge->basis = ellipse;
							} else if (line) {
								edge->basis = line;
							} else if (bspline_curve) {
								edge->basis = bspline_curve;
							}

							if (circle || ellipse) {
								// @todo
								edge->start = 0.;
								edge->end = 2 * boost::math::constants::pi<double>();
							}
							
							auto loop = taxonomy::make<taxonomy::loop>();
							loop->children.push_back(edge);

							face_ = taxonomy::make<taxonomy::face>();
							(*face_)->instance = loop->instance;
							(*face_)->matrix = loop->matrix;
							(*face_)->children = { taxonomy::clone(loop) };
						}
					}
				}

				operator bool() const {
					return face_.is_initialized();
				}

				operator typename T::ptr() const {
					if constexpr (std::is_same_v<T, face>) {
						if (face_) {
							return *face_;
						}
					}
					return nullptr;
				}
			};

            template <typename T>
            class loop_to_piecewise_function_upgrade {
              private:
                boost::optional<taxonomy::piecewise_function::ptr> pwf_;

              public:
               loop_to_piecewise_function_upgrade(taxonomy::ptr item) {
					if constexpr (std::is_same_v<T, piecewise_function>) {
						auto loop = taxonomy::dcast<taxonomy::loop>(item);
						if (loop) {
							if (loop->pwf.is_initialized()) {
								pwf_ = loop->pwf;
							} else {
                        taxonomy::piecewise_function::spans_t spans;
								spans.reserve(loop->children.size());
								for (auto& edge : loop->children) {
									// the edge could be an arc or trimmed circle in the case of IfcIndexPolyCurve - support for this isn't implemented yet
									if (edge->basis) {
										Logger::Message(Logger::Severity::LOG_NOTICE, "Shape of basis curve ignored - edge is treated as a straight line edge");
									}

									const auto& s = boost::get<taxonomy::point3::ptr>(edge->start)->ccomponents();
									const auto& e = boost::get<taxonomy::point3::ptr>(edge->end)->ccomponents();
									Eigen::Vector3d v = e - s;
									auto l = v.norm(); // the norm of a vector is a measure of its length
									v.normalize();     // normalize the vector so that it is a unit direction vector
									std::function<Eigen::Matrix4d(double)> fn = [s, v](double u) {
										Eigen::Vector3d o(s + u * v), axis(0, 0, 1), refDirection(v);
										auto Y = axis.cross(refDirection).normalized();
										axis = refDirection.cross(Y).normalized();
										return taxonomy::make<taxonomy::matrix4>(o, axis, refDirection)->components();
									};
									spans.emplace_back(l, fn);
								}
								pwf_ = taxonomy::make<taxonomy::piecewise_function>(0.0,spans);
								loop->pwf = pwf_;
							}
						}
                    }
                }

                operator bool() const {
                    return pwf_.is_initialized();
                }

                operator typename T::ptr() const {
					if constexpr (std::is_same_v<T, piecewise_function>) {
						if (pwf_) {
							return *pwf_;
						}
					}
					return nullptr;
                }
            };

#ifdef TAXONOMY_USE_SHARED_PTR
			template <typename T, typename U>
			std::shared_ptr<T> cast(const std::shared_ptr<U>& u) {
				{
					curve_to_edge_upgrade<T> upg(u);
					if (upg) {
						return upg;
					}
				}
				{
					curve_to_loop_upgrade<T> upg(u);
					if (upg) {
						return upg;
					}
				}
				{
					edge_to_loop_upgrade<T> upg(u);
					if (upg) {
						return upg;
					}
				}
				{
					curve_to_face_upgrade<T> upg(u);
					if (upg) {
						return upg;
					}
				}
				{
					loop_to_face_upgrade<T> upg(u);
					if (upg) {
						return upg;
					}
				}
				{
					loop_to_piecewise_function_upgrade<T> upg(u);
					if (upg) {
						return upg;
					}
				}
				if (auto r = std::dynamic_pointer_cast<T>(u)) {
					return r;
				} else {
					throw std::runtime_error("Unexpected topology");
				}
			}
			template <typename T, typename U>
			std::shared_ptr<T> dcast(const std::shared_ptr<U>& u) {
				{
					curve_to_edge_upgrade<T> upg(u);
					if (upg) {
						return upg;
					}
				}
				{
					curve_to_face_upgrade<T> upg(u);
					if (upg) {
						return upg;
					}
				}
				{
					edge_to_loop_upgrade<T> upg(u);
					if (upg) {
						return upg;
					}
				}
				{
					loop_to_face_upgrade<T> upg(u);
					if (upg) {
						return upg;
					}
				}
				{
					loop_to_piecewise_function_upgrade<T> upg(u);
					if (upg) {
						return upg;
					}
				}
				return std::dynamic_pointer_cast<T>(u);
			}
#endif
#ifdef TAXONOMY_USE_UNIQUE_PTR
			template <typename T, typename U>
			T* cast(const std::unique_ptr<U>& u) {
				loop_to_face_upgrade<T> upg(u);
				if (upg) {
					return upg;
				}
            loop_to_piecewise_function_upgrade<T> pwupg(u);
            if (pwupg) {
               return pwupg;
            }
            return static_cast<T*>(&*u);
			}
			template <typename T, typename U>
			T* dcast(const std::unique_ptr<U>& u) {
				loop_to_face_upgrade<T> upg(u);
				if (upg) {
					return upg;
				}
            loop_to_piecewise_function_upgrade<T> pwupg(u);
            if (pwupg) {
               return pwupg;
            }
            return dynamic_cast<T*>(&*u);
			}
#endif
#ifdef TAXONOMY_USE_NAKED_PTR
			template <typename T, typename U>
			T* cast(const U*& u) {
				loop_to_face_upgrade<T> upg(u);
				if (upg) {
					return upg;
				}
            loop_to_piecewise_function_upgrade<T> pwupg(u);
            if (pwupg) {
               return pwupg;
            }
            return std::static_cast<T*>(u);
			}
			template <typename T, typename U>
			T* dcast(const U*& u) {
				loop_to_face_upgrade<T> upg(u);
				if (upg) {
					return upg;
				}
            loop_to_piecewise_function_upgrade<T> pwupg(u);
            if (pwupg) {
               return pwupg;
            }
            return std::dynamic_cast<T*>(u);
			}
#endif

		}

		template <typename U, typename Fn>
		void visit(const typename U::ptr& deep, Fn fn) {
			for (auto& i : deep->children) {
				// @todo Sad... now that we have templated collection members,
				// we can't generally use collection_base anymore as a cast target.
				if (auto s = taxonomy::dcast<taxonomy::collection>(i)) {
					visit<taxonomy::collection>(s, fn);
				}
				else if (auto s = taxonomy::dcast<taxonomy::loop>(i)) {
					visit<taxonomy::loop>(s, fn);
				}
				else if (auto s = taxonomy::dcast<taxonomy::face>(i)) {
					visit<taxonomy::face>(s, fn);
				}
				else if (auto s = taxonomy::dcast<taxonomy::shell>(i)) {
					visit<taxonomy::shell>(s, fn);
				}
				else if (auto s = taxonomy::dcast<taxonomy::solid>(i)) {
					visit<taxonomy::solid>(s, fn);
				}
				else if (auto s = taxonomy::dcast<taxonomy::loft>(i)) {
					visit<taxonomy::loft>(s, fn);
				}
				else if (auto s = taxonomy::dcast<taxonomy::boolean_result>(i)) {
					visit<taxonomy::boolean_result>(s, fn);
				}
				else {
					fn(i);
				}
			}
		}

		template <typename T, typename U, typename Fn>
		void visit_2(const typename U::ptr& c, const Fn& fn) {
			static_assert(std::is_same<T, taxonomy::point3>::value, "@todo Only implemented for point3");
			for (auto& i : c->children) {
				// @todo Sad... now that we have templated collection members,
				// we can't generally use collection_base anymore as a cast target.
				if (auto s = taxonomy::dcast<taxonomy::collection>(i)) {
					visit_2<T, taxonomy::collection>(s, fn);
				}
				else if (auto s = taxonomy::dcast<taxonomy::loop>(i)) {
					visit_2<T, taxonomy::loop>(s, fn);
				}
				else if (auto s = taxonomy::dcast<taxonomy::face>(i)) {
					visit_2<T, taxonomy::face>(s, fn);
				}
				else if (auto s = taxonomy::dcast<taxonomy::shell>(i)) {
					visit_2<T, taxonomy::shell>(s, fn);
				}
				else if (auto s = taxonomy::dcast<taxonomy::solid>(i)) {
					visit_2<T, taxonomy::solid>(s, fn);
				}
				else if (auto s = taxonomy::dcast<taxonomy::loft>(i)) {
					visit_2<T, taxonomy::loft>(s, fn);
				}
				else if (auto s = taxonomy::dcast<taxonomy::boolean_result>(i)) {
					visit_2<T, taxonomy::boolean_result>(s, fn);
				}
				else if (auto pt = taxonomy::dcast<taxonomy::point3>(i)) {
					fn(pt);
				}
				else if (auto l = taxonomy::dcast<taxonomy::edge>(i)) {
					// @todo maybe make edge a collection then as well?
					if (l->start.which() == 1) {
						fn(boost::get<taxonomy::point3::ptr>(l->start));
					}
					if (l->end.which() == 1) {
						fn(boost::get<taxonomy::point3::ptr>(l->end));
					}
				}
			}
		}

		taxonomy::collection::ptr flatten(const taxonomy::collection::ptr& deep);

		template <typename Fn>
		bool apply_predicate_to_collection(const taxonomy::ptr& i, Fn fn) {
			if (i->kind() == taxonomy::COLLECTION) {
				auto c = taxonomy::cast<taxonomy::collection>(i);
				for (auto& child : c->children) {
					if (apply_predicate_to_collection(child, fn)) {
						return true;
					}
				}
				return false;
			}
			else {
				return fn(i);
			}
		}

		// @nb traverses nested collections
		template <typename Fn>
		taxonomy::collection::ptr filter(const taxonomy::collection::ptr& collection, Fn fn) {
			auto filtered = taxonomy::make<taxonomy::collection>();
			for (auto& child : collection->children) {
				if (apply_predicate_to_collection(child, fn)) {
					filtered->children.push_back(clone(child));
				}
			}
			if (filtered->children.empty()) {
#ifdef TAXONOMY_USE_NAKED_PTR
				delete filtered;
#endif
				return nullptr;
			}
			return filtered;
		}

		// @nb traverses nested collections
		template <typename Fn>
		taxonomy::collection::ptr filter_in_place(taxonomy::collection::ptr collection, Fn fn) {
			auto& c = collection->children;
			auto new_end = std::remove_if(c.begin(), c.end(), [fn](taxonomy::geom_item::ptr i) {
				return !apply_predicate_to_collection(i, fn);
			});
#ifdef TAXONOMY_USE_NAKED_PTR
			for (auto it = new_end; it != c.end(); ++it) {
				delete *it;
			}
#endif
			c.erase(new_end, c.end());
			return collection;
		}

		taxonomy::solid::ptr create_box(double dx, double dy, double dz);
		taxonomy::solid::ptr create_box(double x, double y, double z, double dx, double dy, double dz);

		struct layerset_information {
			std::vector<double> thicknesses;
			std::vector<ifcopenshell::geometry::taxonomy::ptr> layers;
			std::vector<ifcopenshell::geometry::taxonomy::style> styles;
		};

		enum connection_type {
			ATPATH,
			ATSTART,
			ATEND,
			NOTDEFINED
		};

		typedef std::tuple<connection_type, connection_type, IfcUtil::IfcBaseEntity*> endpoint_connection;
	}

}

#endif