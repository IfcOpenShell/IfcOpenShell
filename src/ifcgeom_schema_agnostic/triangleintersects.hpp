#ifndef THREEYD_MOELLER_TRIANGLEINTERSECTS_HPP
#define THREEYD_MOELLER_TRIANGLEINTERSECTS_HPP

#include <algorithm>
#include <array>
#include <cassert>
#include <cmath>
#include <cstdlib>
#include <iterator>
#include <stdexcept>
#include <type_traits>

/**
 * Single header mplementation of Triangle-Triangle and Triangle-Box intersection tests by Tomas Akenine Moeller
 * @see http://fileadmin.cs.lth.se/cs/Personal/Tomas_Akenine-Moller/code/tribox3.txt
 * @see http://fileadmin.cs.lth.se/cs/Personal/Tomas_Akenine-Moller/code/tritri_isectline.txt
 */

namespace threeyd
{
namespace moeller
{
namespace detail
{
static constexpr float MATH_PI = 3.f;

template <typename...>
using void_t = void;

template <class T, class Index, typename = void>
struct HasSubscriptOperator : std::false_type
{
};

template <class T, class Index>
struct HasSubscriptOperator<T, Index, void_t<decltype(std::declval<T>()[std::declval<Index>()])>> : std::true_type
{
};

// Provides universal, run-time-modifiable "tolerance" for all instances of class TriangleIntersects template.
// This concrete class simplifies initialization and storage allocation of "tolerance"
class Tolerance
{
    static constexpr float value = 1e-6f;

  public:
    static constexpr float get_value() { return value; }
};

enum class Coplanarity
{
    YES,
    MAYBE,
    NO
};

template <typename T>
void clip_to_01(T& x)
{
    constexpr T ONE = static_cast<T>(1.0f);
    constexpr T ZERO = T();

    if (x > ONE)
    {
        x = ONE;
    }
    else if (x < ZERO)
    {
        x = ZERO;
    }
}

// solves symmetric, positive definite system of 2 linear equations for x, y:
// a00 * x + a01 * y = b0
// a01 * x + a11 * y = b1
// returns 1, if exactly one solution exists, or -1 if the equations have infinite nuber of solutions
// Caveat: in WTA, the equations solved with this function always have at least one solution
template <typename T>
void solve_spd_linear_equations(T& x, T& y, bool& is_solution_unique, double a00, double a01, double a11, double b0,
                                double b1)
{
    // epsilon  corresponds to two lines considered parallel if the angle between them is less than 1 tenth of degree
    // 1/10 degree = 1.75e-3 radian, and 1.75e-3 squared yields 3e-6
    const double epsilon = 3e-6;

    assert(a00 >= 1e-8);  // 1e-8 is the square of the minimal length of a face side
    assert(a11 >= 1e-8);

    // scale the equations so that the matrix diagonal elements = 1.0
    auto a10 = a01;
    a01 /= a00;
    b0 /= a00;

    a10 /= a11;
    b1 /= a11;

    // now det(A) = 1 - cos(alpha)^2 \approx alpha^2 > 0
    // where alpha is the angle between the two lines whose intersection is searched for
    double det = 1.0 - a01 * a10;
    double enum_x = b0 - b1 * a01;
    double enum_y = b1 - b0 * a10;

    // in exact arithmetics, 'det' cannot be negative; but we must take into account floating-point errors
    if (det < -1e-4)
    {
        throw std::logic_error{};
    }
    if (det < 0.0)
    {
        det = 0.0;
    }

    is_solution_unique = (det >= epsilon);
    if (is_solution_unique)
    {
        x = enum_x / det;
        y = enum_y / det;
    }
    else
    {
        // perhaps the lines are not strictly parallel: let's try to find the "exact" solution anyway
        if (det > 1e-20)
        {
            x = enum_x / det;
            y = enum_y / det;
        }
        else  // don't use det, as it is too close to 0
        {
            x = 0;
            y = b0 / a01;
        }
    }
}
}  // namespace detail

/**
 * @param TemplatedVec is any random-access 3-element container with operator[] returning a floating-point type
 *
 * Provides bool moeller:TriangleIntersects<T>::triangle(T v1, T v2, T v3, T u1, T u2, T u3);
 * Provides bool moeller:TriangleIntersects<T>::triangle(T v1, T v2, T v3, T u1, T u2, T u3, T out_inters_endpoint1,
 *  T out_inters_endpoint2, bool out_is_coplanar);
 * Provides bool moeller:TriangleIntersects<T>::box(T v1, T v2, T v3, T boxCenter, T boxHalfSize);
 */

template <typename TemplatedVec>
class TriangleIntersects
{
    using Triangle = std::array<TemplatedVec, 3>;

    static_assert(detail::HasSubscriptOperator<TemplatedVec, size_t>::value, "TemplatedVec must implement operator[]");
    using declfloat = typename std::decay<decltype(std::declval<TemplatedVec>()[0])>::type;

  public:
    // distances smaller than get_tolerance() may be treated as 0
    static declfloat get_tolerance() { return detail::Tolerance::get_value(); }

    // angles smaller than this constant are candidates for coplanarity test
    static constexpr declfloat DEFAULT_COPLANARITY_THRESHOLD_ANGLE = 0.1f;  // wilde guess, so far

    // Angles smaller than the constant below are used for additional test for not self intersecting
    // The value of 60 degress reduces the number of self-intersecting faces reported by this module.
    // whether 60, 85 or 45 or other value is better is a question of priorities.
    // The difference is in the accuracy of the software to detect that two triangle *nearly* touch each other
    static constexpr declfloat DEFAULT_INTERSECTION_TEST_THRESHOLD_ANGLE = 60.0f;  // wilde guess, so far

    static_assert(
        DEFAULT_COPLANARITY_THRESHOLD_ANGLE < 5,
        "default_coplanarity_threshold_angle must be small enough so that that it doesn't differ much from its sinus ");
    static_assert(DEFAULT_INTERSECTION_TEST_THRESHOLD_ANGLE < 89,
                  "default_intersection_test_threshold_angle out of range");

    static constexpr double COPLANARITY_THRESHOLD_IN_DEGREES = DEFAULT_COPLANARITY_THRESHOLD_ANGLE;
    static constexpr double COPLANARITY_THRESHOLD = detail::MATH_PI / 180.0 * COPLANARITY_THRESHOLD_IN_DEGREES;
    static constexpr double COPLANARITY_THRESHOLD_SQUARED = COPLANARITY_THRESHOLD * COPLANARITY_THRESHOLD;

    static constexpr double sin_approximated(double x)
    {
        return x - x * x * x / 6.0 + x * x * x * x * x / 120.0;  // approximates sin(x)
    }

    static constexpr double INTERSECTION_TEST_THRESHOLD =
        sin_approximated(detail::MATH_PI / 180.0 * DEFAULT_INTERSECTION_TEST_THRESHOLD_ANGLE);
    static constexpr double INTERSECTION_TEST_THRESHOLD_SQUARED =
        INTERSECTION_TEST_THRESHOLD * INTERSECTION_TEST_THRESHOLD;

    // returns true iff two triangles are intersecting or touching
    // actually does not seem to be used in WTA
    static bool triangle(const TemplatedVec& firstV1, const TemplatedVec& firstV2, const TemplatedVec& firstV3,
                         const TemplatedVec& secondV1, const TemplatedVec& secondV2, const TemplatedVec& secondV3)
    {
        TemplatedVec intersection_line_end_point1;
        TemplatedVec intersection_line_end_point2;
        detail::Coplanarity coplanarity;
        return tri_tri_intersect_with_isectline(firstV1, firstV2, firstV3, secondV1, secondV2, secondV3, coplanarity,
                                                intersection_line_end_point1, intersection_line_end_point2, false,
                                                0);  // assuming that no vertices are shared
    }

    // similar to the previous function, but returns additional information
    // on the intersection line in the case of non-parllel triangles
    // and whether the two triangles are coplanar (in which case the intersection line is undefined)
    static bool triangle(const TemplatedVec& firstV1, const TemplatedVec& firstV2, const TemplatedVec& firstV3,
                         const TemplatedVec& secondV1, const TemplatedVec& secondV2, const TemplatedVec& secondV3,
                         TemplatedVec& IntersectionLineEndPoint1, TemplatedVec& IntersectionLineEndPoint2,
                         bool& coplanar)
    {
        detail::Coplanarity coplanarity;
        bool result =
            tri_tri_intersect_with_isectline(firstV1, firstV2, firstV3, secondV1, secondV2, secondV3, coplanarity,
                                             IntersectionLineEndPoint1, IntersectionLineEndPoint2, true, 0);
        if (detail::Coplanarity::YES == coplanarity)
        {
            coplanar = true;
        }
        else if (detail::Coplanarity::NO == coplanarity)
        {
            coplanar = false;
        }
        return result;
    }

    // tests if a triangle intersects a box with its faces parallel to the x-y-z Cartesian axis
    static bool box(const TemplatedVec& triangleV1, const TemplatedVec& triangleV2, const TemplatedVec& triangleV3,
                    const TemplatedVec& boxCenter, const TemplatedVec& boxHalfSize)
    {
        return tri_box_overlap(triangleV1, triangleV2, triangleV3, boxCenter, boxHalfSize);
    }

    bool static is_wedge_colinear(const TemplatedVec& EU1, const TemplatedVec& EU2,
                                  float tolerance = detail::Tolerance::get_value() / 10.0f)
    {
        auto surface_u = 0.5f * EU1.cross(EU2).abs();
        auto max_side_u = std::max({(EU2 - EU1).abs(), EU1.abs(), EU2.abs()});
        auto min_height_u = surface_u / max_side_u;
        return min_height_u < tolerance;
    }

    // The function returns a vector to a line defined by LineVec
    // N is a vector normal to another (reference) plane
    // N is the preferred result
    static TemplatedVec normal_to_line_and_within_plane(TemplatedVec N, TemplatedVec LineVec)
    {
        normalize(LineVec);
        auto d = std::abs(dot(LineVec, N));
        if (d < 1e-8)
        {  // N is orthogonal do LineVec
            return N;
        }

        int idx = index_into_smallest_component_abs(LineVec);
        TemplatedVec n0{static_cast<float>(idx == 0), static_cast<float>(idx == 1), static_cast<float>(idx == 2)};
        TemplatedVec result;
        cross(result, n0, LineVec);
        return result;
    }

  private:
    struct Triplet
    {
        declfloat x;  // x-coordinate
        declfloat w;  // weight
        int idx;      // identifier of the segment's end, 0 or 1
        bool operator<(const Triplet& rhs) const { return x < rhs.x; }
    };

    // Constants definitions
    static constexpr size_t X = 0;
    static constexpr size_t Y = 1;
    static constexpr size_t Z = 2;

    // Helper methods

    // returns the index into the the largest-magnitude component of the argument
    inline static unsigned index_into_largest_component_abs(const TemplatedVec& D)
    {
        declfloat a = fabs(D[0]);
        declfloat b = fabs(D[1]);
        declfloat c = fabs(D[2]);

        if (a < b)
        {
            if (b < c)
            {
                return 2;  // c is largest
            }
            {
                return 1;  // b is largest
            }
        }
        else
        {
            if (a < c)
            {
                return 2;  // c is largest
            }
            {
                return 0;  // a is largest
            }
        }
    }

    // returns the index into the the largest-magnitude component of the argument
    inline static unsigned index_into_smallest_component_abs(const TemplatedVec& D)
    {
        declfloat a = fabs(D[0]);
        declfloat b = fabs(D[1]);
        declfloat c = fabs(D[2]);

        if (a < b)
        {
            if (a < c)
            {
                return 0;  // a is largest
            }
            {
                return 2;  // c is largest
            }
        }
        else
        {
            if (b < c)
            {
                return 1;  // b is smallest
            }
            {
                return 2;  // c is smallest
            }
        }
    }

    /*
    static unsigned index_into_largest_component_abs(std::array<declfloat, 3> V)
    {
        return index_into_largest_component_abs(TemplatedVec{V[0], V[1], V[2]});
    }
    */

    // cross product
    inline static void cross(TemplatedVec& dest, const TemplatedVec& v1, const TemplatedVec& v2)
    {
        dest[X] = v1[Y] * v2[Z] - v1[Z] * v2[Y];
        dest[Y] = v1[Z] * v2[X] - v1[X] * v2[Z];
        dest[Z] = v1[X] * v2[Y] - v1[Y] * v2[X];
    }

    inline static TemplatedVec guarded_cross_product(const TemplatedVec& v1, const TemplatedVec& v2)
    {
        constexpr declfloat MACHINE_EPSILON_F = std::numeric_limits<declfloat>::epsilon();
        TemplatedVec product;
        cross(product, v1, v2);
        using std::abs;
        if (abs(product[0]) < (abs(v1[1] * v2[2]) + abs(v2[1] * v1[2])) * MACHINE_EPSILON_F)
        {
            product[0] = 0;
        }
        if (abs(product[1]) < (abs(v1[2] * v2[0]) + abs(v2[2] * v1[0])) * MACHINE_EPSILON_F)
        {
            product[1] = 0;
        }
        if (abs(product[2]) < (abs(v1[0] * v2[1]) + abs(v2[0] * v1[1])) * MACHINE_EPSILON_F)
        {
            product[2] = 0;
        }
        return product;
    }

    // dot product
    inline static declfloat dot(const TemplatedVec& v1, const TemplatedVec& v2)
    {
        return v1[X] * v2[X] + v1[Y] * v2[Y] + v1[Z] * v2[Z];
    }

    inline static declfloat norm(const TemplatedVec& v) { return sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]); }

    // vector normalization
    inline static bool normalize(TemplatedVec& v)
    {
        constexpr double ZERO_LENGTH_THRESHOLD = 1e-20;
        double d_norm = norm(v);
        if (d_norm > ZERO_LENGTH_THRESHOLD)
        {
            v[0] /= d_norm;
            v[1] /= d_norm;
            v[2] /= d_norm;
            return true;
        }
        return false;
    }
    // vector subtraction
    inline static void sub(TemplatedVec& dest, const TemplatedVec& v1, const TemplatedVec& v2)
    {
        dest[X] = v1[X] - v2[X];
        dest[Y] = v1[Y] - v2[Y];
        dest[Z] = v1[Z] - v2[Z];
    }
    // vector addition
    inline static void add(TemplatedVec& dest, const TemplatedVec& v1, const TemplatedVec& v2)
    {
        dest[X] = v1[X] + v2[X];
        dest[Y] = v1[Y] + v2[Y];
        dest[Z] = v1[Z] + v2[Z];
    }
    // vector product by scalar
    inline static void mult(TemplatedVec& dest, const TemplatedVec& v, const declfloat factor)
    {
        dest[X] = factor * v[X];
        dest[Y] = factor * v[Y];
        dest[Z] = factor * v[Z];
    }
    // assignment
    inline static void set(TemplatedVec& dest, const TemplatedVec& src)
    {
        dest[X] = src[X];
        dest[Y] = src[Y];
        dest[Z] = src[Z];
    }

    inline static void find_min_max(const declfloat x0, const declfloat x1, const declfloat x2, declfloat& min,
                                    declfloat& max)
    {
        min = std::min(std::min(x0, x1), x2);
        max = std::max(std::max(x0, x1), x2);
    }

    // Tests for Box-Triangle
    inline static bool axis_test_x01(const TemplatedVec& v0, const TemplatedVec& v2, const TemplatedVec& boxhalfsize,
                                     const declfloat a, const declfloat b, const declfloat fa, const declfloat fb,
                                     declfloat& min, declfloat& max, declfloat& rad)
    {
        declfloat p0 = a * v0[Y] - b * v0[Z];
        declfloat p2 = a * v2[Y] - b * v2[Z];
        if (p0 < p2)
        {
            min = p0;
            max = p2;
        }
        else
        {
            min = p2;
            max = p0;
        }
        rad = fa * boxhalfsize[Y] + fb * boxhalfsize[Z];
        return !static_cast<bool>(min > rad || max < -rad);
    }
    inline static bool axis_test_x2(const TemplatedVec& v0, const TemplatedVec& v1, const TemplatedVec& boxhalfsize,
                                    const declfloat a, const declfloat b, const declfloat fa, const declfloat fb,
                                    declfloat& min, declfloat& max, declfloat& rad)
    {
        declfloat p0 = a * v0[Y] - b * v0[Z];
        declfloat p1 = a * v1[Y] - b * v1[Z];
        if (p0 < p1)
        {
            min = p0;
            max = p1;
        }
        else
        {
            min = p1;
            max = p0;
        }
        rad = fa * boxhalfsize[Y] + fb * boxhalfsize[Z];
        return !static_cast<bool>(min > rad || max < -rad);
    }
    inline static bool axis_test_y02(const TemplatedVec& v0, const TemplatedVec& v2, const TemplatedVec& boxhalfsize,
                                     const declfloat a, const declfloat b, const declfloat fa, const declfloat fb,
                                     declfloat& min, declfloat& max, declfloat& rad)
    {
        declfloat p0 = -a * v0[X] + b * v0[Z];
        declfloat p2 = -a * v2[X] + b * v2[Z];
        if (p0 < p2)
        {
            min = p0;
            max = p2;
        }
        else
        {
            min = p2;
            max = p0;
        }
        rad = fa * boxhalfsize[X] + fb * boxhalfsize[Z];
        return !static_cast<bool>(min > rad || max < -rad);
    }
    inline static bool axis_test_y1(const TemplatedVec& v0, const TemplatedVec& v1, const TemplatedVec& boxhalfsize,
                                    const declfloat a, const declfloat b, const declfloat fa, const declfloat fb,
                                    declfloat& min, declfloat& max, declfloat& rad)
    {
        declfloat p0 = -a * v0[X] + b * v0[Z];
        declfloat p1 = -a * v1[X] + b * v1[Z];
        if (p0 < p1)
        {
            min = p0;
            max = p1;
        }
        else
        {
            min = p1;
            max = p0;
        }
        rad = fa * boxhalfsize[X] + fb * boxhalfsize[Z];
        return !static_cast<bool>(min > rad || max < -rad);
    }
    inline static bool axis_test_z12(const TemplatedVec& v1, const TemplatedVec& v2, const TemplatedVec& boxhalfsize,
                                     const declfloat a, const declfloat b, const declfloat fa, const declfloat fb,
                                     declfloat& min, declfloat& max, declfloat& rad)
    {
        declfloat p1 = a * v1[X] - b * v1[Y];
        declfloat p2 = a * v2[X] - b * v2[Y];
        if (p2 < p1)
        {
            min = p2;
            max = p1;
        }
        else
        {
            min = p1;
            max = p2;
        }
        rad = fa * boxhalfsize[X] + fb * boxhalfsize[Y];
        return !static_cast<bool>(min > rad || max < -rad);
    }
    inline static bool axis_test_z0(const TemplatedVec& v0, const TemplatedVec& v1, const TemplatedVec& boxhalfsize,
                                    const declfloat a, const declfloat b, const declfloat fa, const declfloat fb,
                                    declfloat& min, declfloat& max, declfloat& rad)
    {
        declfloat p0 = a * v0[X] - b * v0[Y];
        declfloat p1 = a * v1[X] - b * v1[Y];
        if (p0 < p1)
        {
            min = p0;
            max = p1;
        }
        else
        {
            min = p1;
            max = p0;
        }
        rad = fa * boxhalfsize[X] + fb * boxhalfsize[Y];
        return !static_cast<bool>(min > rad || max < -rad);
    }

    /********************************************
     * Tests for Triangle-Triangle intersection *
     ********************************************/

    // Tests whether edge U0, U1 intersects with the edge whose origin is V0 and the coordinates
    // of the vector pointing towards the second vertex are Ax (along i0 axis) and Ay (along i1 axis).
    // A = V1 - V0
    // i0 stands for the "x" axis and "i1" for the "y" axis in the new (local) coordinate system.
    // The vertices are projected onto the i0-i1 plane before the actual intersection detection is performed
    //
    // Caveat! This test most likely fails if the two edges ar colinear
    // But this doesn't disturb the final result (other tests should detect the intersection)
    inline static bool edge_edge_test(const TemplatedVec& V0, const TemplatedVec& U0, const TemplatedVec& U1,
                                      const size_t i0, const size_t i1, declfloat Ax, declfloat Ay)
    {
        constexpr declfloat TOLERANCE = 1e-10;
        declfloat bx, by, cx, cy, f, d, e;
        bx = U0[i0] - U1[i0];  // B = U0 - U1 (projected onto the i0-i1 plane)
        by = U0[i1] - U1[i1];
        cx = V0[i0] - U0[i0];  // C = V0 - U0 (projected onto the i0-i1 plane)
        cy = V0[i1] - U0[i1];
        // if the edges intersect, |f| is twice the area of the convex quadrilateral spanned by the vertices
        f = Ay * bx - Ax * by;
        // if the edges intersect, |d| is twice the area of the triangle U0, U1, V0
        d = by * cx - bx * cy;
        if ((f > 0 && d >= 0 && d <= f) || (f < 0 && d <= 0 && d >= f))
        {
            // if the edges intersect, |e| is twice the area of the triangle V0, V1, U0
            e = Ax * cy - Ay * cx;
            if (f > 0)
            {
                if (e >= 0 && e <= f)
                {
                    return true;
                }
            }
            else
            {
                if (e <= 0 && e >= f)
                {
                    return true;
                }
            }
        }
        // all Vertices are colinear iff f == 0 and d == 0
        if (std::abs(d) < TOLERANCE && std::abs(f) < TOLERANCE)
        {
            // Let B = U1 - U0
            bx = -bx;
            by = -by;
            // Let A = V1 - U0;
            Ax += cx;
            Ay += cy;
            // Now B = U1 - U0, A = V1 - U0, C = V0 - U0, so we have 3 points realtive to U0.
            // Let's test if [(0,0), B] overlaps with [A, C]
            if (std::abs(by) > std::abs(bx))
            {
                std::swap(Ax, Ay);
                std::swap(bx, by);
                std::swap(cx, cy);
            }
            // Now it suffices to inspect the projection on the x axis
            if (cx < Ax)
            {
                std::swap(Ax, cx);
            }
            return Ax < bx && cx > 0;
        }
        return false;
    }

    // V0, V1 define an edge
    // U0, U1, U2 define a triangle
    // i0, i1 \in {0,1,2} define the plane (x-y, x-z or y-z) onto which all five vertices are projected
    inline static bool edge_against_tri_edge(const TemplatedVec& V0, const TemplatedVec& V1, const TemplatedVec& U0,
                                             const TemplatedVec& U1, const TemplatedVec& U2, const size_t i0,
                                             const size_t i1)
    {
        declfloat ax, ay;  // coordinates of the edge relative to  V0

        ax = V1[i0] - V0[i0];
        ay = V1[i1] - V0[i1];
        /* test intersection of edge U0, U1 with edge V0, V1 */
        if (edge_edge_test(V0, U0, U1, i0, i1, ax, ay))
        {
            return true;
        }
        /* test edge U1,U2 against V1 - V0 */
        if (edge_edge_test(V0, U1, U2, i0, i1, ax, ay))
        {
            return true;
        }
        /* test edge U2,U1 against V1 - V0 */
        if (edge_edge_test(V0, U2, U0, i0, i1, ax, ay))
        {
            return true;
        }
        return false;
    }

    // Computes extreme intersection points (endpoints) between a triangle and the plane of another triangle.
    // It must have been already established that such intersection exists.
    // It is assumed that V0 is on the other side of the plane than V1 and V2
    //  so that segments V0-V1 and V0-V2 intersect the plane (some, but not all of them may lie on the plane itself)
    // The algorithm is based on similarity of triangles (Thales theorem)
    //
    // CAVEAT! How this function can possibly work correctly if d0, d1 and d2 can hold the incorrect value of 0
    //  if their actual value magnitudes are < EPSILON?
    // Unmodified triangle A "sees" modified triangle B, and unmodified triangle B "sees" modified triangle A
    //  how can this be correct for general triangles A,B?
    inline static void isect2(const TemplatedVec& V0,    // vertex 0
                              const TemplatedVec& V1,    // vertex 1
                              const TemplatedVec& V2,    // vertex 2
                              const declfloat x0,        // projection of vetrex 0 on the "safe" axis (x, y, or z)
                              const declfloat x1,        // -,,-          vertex 1
                              const declfloat x2,        // -,,-          vertex 2
                              const declfloat d0,        // signed distance of vertex 0 from the other plane
                              const declfloat d1,        // -,,-               vertex 1
                              const declfloat d2,        // -,,-               vertex 2
                              declfloat& endpoint_x_0,   // intersection endpoint 0 on the "safe" axsis
                              declfloat& endpoint_x_1,   // intersection endpoint 1 on the "safe" axsis
                              TemplatedVec& Endpoint_0,  // intersection endpoint 0 in 3D
                              TemplatedVec& Endpoint_1)  // intersection endpoint 1 in 3D
    {
        assert(d0 != d1);  // moreover, d0 and d1 must have different signs: +, 0 or -
        assert(d0 != d2);  // moreover, d0 and d2 must have different signs: +, 0 or -

        std::array<Triplet, 2> x_w_pairs;
        declfloat w = d0 / (d0 - d1);
        detail::clip_to_01(w);
        declfloat x = x0 + (x1 - x0) * w;
        x_w_pairs[0] = Triplet{x, w, 0};
        w = d0 / (d0 - d2);
        detail::clip_to_01(w);
        x = x0 + (x2 - x0) * w;
        x_w_pairs[1] = Triplet{x, w, 1};

        if (x_w_pairs[1] < x_w_pairs[0])
        {
            std::swap(x_w_pairs[0], x_w_pairs[1]);
        }

        endpoint_x_0 = x_w_pairs[0].x;
        endpoint_x_1 = x_w_pairs[1].x;

        w = x_w_pairs[0].w;
        int idx = x_w_pairs[0].idx;
        TemplatedVec v_other = (idx == 0) ? V1 : V2;

        TemplatedVec displacement;
        sub(displacement, v_other, V0);
        mult(displacement, displacement, w);  // Displacement = w * (V1 - V0)
        add(Endpoint_0, displacement, V0);    // Endpoint_0 = V0 + w * (V1 - V0)

        w = x_w_pairs[1].w;
        idx = x_w_pairs[1].idx;
        v_other = (idx == 0) ? V1 : V2;
        sub(displacement, v_other, V0);
        mult(displacement, displacement, w);
        add(Endpoint_1, V0, displacement);  // Endpoint_1 = V0 + w *(V2 - V0)
    }

    // Similar to isect2, but called when it is certain that V0 is the shared vertex
    // and neither V1 nor V2 lies closer to the target plane than detail::Tolerance::get_value()
    // There's no way to verify this condition within the function
    inline static void isect2_shared_at_v0  //
        (const TemplatedVec& V0,            // vertex 0
         const declfloat x0,                // projection of vertex 0 on the "safe" axis (x, y, or z)
         declfloat& endpoint_x_0,           // intersection endpoint 0 on the "safe" axsis
         declfloat& endpoint_x_1,           // intersection endpoint 1 on the "safe" axsis
         TemplatedVec& Endpoint_0,          // intersection endpoint 0 in 3D
         TemplatedVec& Endpoint_1           // intersection endpoint 1 in 3D
        )
    {
        endpoint_x_0 = endpoint_x_1 = x0;
        Endpoint_0 = Endpoint_1 = V0;
    }

    // Similar to isect2, but called when it is certain that V1 is the shared vertex
    // There's no way to verify this condition within the function
    inline static void isect2_shared_at_v1  //
        (const TemplatedVec& V0,            // vertex 0
         const TemplatedVec& V1,            // vertex 1
         const TemplatedVec& V2,            // vertex 2
         const declfloat x0,                // projection of vertex 0 on the "safe" axis (x, y, or z)
         const declfloat x1,                // -,,-          vertex 1
         const declfloat x2,                // -,,-          vertex 2
         declfloat d0,                      // signed distance of vertex 0 from the other plane
         declfloat d2,                      // -,,-               vertex 2
         declfloat& endpoint_x_0,           // intersection endpoint 0 on the "safe" axsis
         declfloat& endpoint_x_1,           // intersection endpoint 1 on the "safe" axsis
         TemplatedVec& Endpoint_0,          // intersection endpoint 0 in 3D
         TemplatedVec& Endpoint_1)          // intersection endpoint 1 in 3D

    {
        // d0 and d2 must have different signs: +, 0 or -
        if (d0 * d2 > 0)
        {
            // here either d0 or d2 must be small, hardly distingusihable from 0;
            assert(std::abs(d0) <= detail::Tolerance::get_value() || std::abs(d2) <= detail::Tolerance::get_value());
            if (fabs(d0) < fabs(d2))
            {
                d0 = 0;
            }
            else
            {
                d2 = 0;
            }
        }

        std::array<Triplet, 3> x_w_pairs;
        unsigned arr_idx = 0;
        x_w_pairs[arr_idx++] = Triplet{x1, 1.0, 0};
        if (std::abs(d0) < detail::Tolerance::get_value())
        {
            x_w_pairs[arr_idx++] = Triplet{x0, 0.0, 0};
        }

        if (std::abs(d2) < detail::Tolerance::get_value())
        {
            x_w_pairs[arr_idx++] = Triplet{x2, 1.0, 1};
        }
        else
        {
            declfloat w = d0 / (d0 - d2);  // weight, between 0 and 1
            detail::clip_to_01(w);
            declfloat x = x0 + (x2 - x0) * w;
            x_w_pairs[arr_idx++] = Triplet{x, w, 1};
        }

        assert(arr_idx <= 3);
        auto p = std::minmax_element(x_w_pairs.begin(), x_w_pairs.begin() + arr_idx);
        endpoint_x_0 = p.first->x;
        endpoint_x_1 = p.second->x;

        declfloat w = p.first->w;
        int idx = p.first->idx;
        TemplatedVec v_other = (idx == 0) ? V1 : V2;

        TemplatedVec displacement;
        sub(displacement, v_other, V0);
        mult(displacement, displacement, w);  // Displacement = w * (V1 - V0)
        add(Endpoint_0, displacement, V0);    // Endpoint_0 = V0 + w * (V1 - V0)

        w = p.second->w;
        idx = p.second->idx;
        v_other = (idx == 0) ? V1 : V2;
        sub(displacement, v_other, V0);
        mult(displacement, displacement, w);
        add(Endpoint_1, V0, displacement);  // Endpoint_1 = V0 + w *(V2 - V0)
    }

    inline static bool point_in_tri(const TemplatedVec& V0, const TemplatedVec& U0, const TemplatedVec& U1,
                                    const TemplatedVec& U2, const size_t i0, const size_t i1)
    {
        declfloat a, b, c, d0, d1, d2;
        /* is T1 completly inside T2? */
        /* check if V0 is inside tri(U0,U1,U2) */
        a = U1[i1] - U0[i1];
        b = -(U1[i0] - U0[i0]);
        c = -a * U0[i0] - b * U0[i1];
        d0 = a * V0[i0] + b * V0[i1] + c;

        a = U2[i1] - U1[i1];
        b = -(U2[i0] - U1[i0]);
        c = -a * U1[i0] - b * U1[i1];
        d1 = a * V0[i0] + b * V0[i1] + c;

        a = U0[i1] - U2[i1];
        b = -(U0[i0] - U2[i0]);
        c = -a * U2[i0] - b * U2[i1];
        d2 = a * V0[i0] + b * V0[i1] + c;

        if (d0 * d1 > 0.0)
        {
            if (d0 * d2 > 0.0)
            {
                return true;
            }
        }
        return false;
    }

    // Private methods
    static bool plane_box_overlap(const TemplatedVec& normal, const TemplatedVec& vert,
                                  const TemplatedVec& maxbox)  // -NJMP-
    {
        size_t q;
        declfloat v;
        TemplatedVec vmin, vmax;
        for (q = X; q <= Z; q++)
        {
            v = vert[q];
            if (normal[q] > 0.0f)
            {
                vmin[q] = -maxbox[q] - v;
                vmax[q] = maxbox[q] - v;
            }
            else
            {
                vmin[q] = maxbox[q] - v;
                vmax[q] = -maxbox[q] - v;
            }
        }
        if (dot(normal, vmin) > 0.0f)
        {
            return false;
        }
        return static_cast<bool>(dot(normal, vmax) >= 0.0f);
    }

    static bool tri_box_overlap(const TemplatedVec& trivert0, const TemplatedVec& trivert1,
                                const TemplatedVec& trivert2, const TemplatedVec& boxcenter,
                                const TemplatedVec& boxhalfsize)
    {
        /*    use separating axis theorem to test overlap between triangle and box */
        /*    need to test for overlap in these directions: */
        /*    1) the {x,y,z}-directions (actually, since we use the AABB of the triangle */
        /*       we do not even need to test these) */
        /*    2) normal of the triangle */
        /*    3) crossproduct(edge from tri, {x,y,z}-directin) */
        /*       this gives 3x3=9 more tests */

        TemplatedVec v0, v1, v2;
        declfloat min, max, rad, fex, fey, fez;
        TemplatedVec normal, e0, e1, e2;
        /* This is the fastest branch on Sun */
        /* move everything so that the boxcenter is in (0,0,0) */
        sub(v0, trivert0, boxcenter);
        sub(v1, trivert1, boxcenter);
        sub(v2, trivert2, boxcenter);
        /* compute triangle edges */
        sub(e0, v1, v0); /* tri edge 0 */
        sub(e1, v2, v1); /* tri edge 1 */
        sub(e2, v0, v2); /* tri edge 2 */

        /* Bullet 3:  */
        /*  test the 9 tests first (this was faster) */
        fex = fabsf(e0[X]);
        fey = fabsf(e0[Y]);
        fez = fabsf(e0[Z]);

        if (!axis_test_x01(v0, v2, boxhalfsize, e0[Z], e0[Y], fez, fey, min, max, rad))
        {
            return false;
        }
        if (!axis_test_y02(v0, v2, boxhalfsize, e0[Z], e0[X], fez, fex, min, max, rad))
        {
            return false;
        }
        if (!axis_test_z12(v1, v2, boxhalfsize, e0[Y], e0[X], fey, fex, min, max, rad))
        {
            return false;
        }

        fex = fabsf(e1[X]);
        fey = fabsf(e1[Y]);
        fez = fabsf(e1[Z]);

        if (!axis_test_x01(v0, v2, boxhalfsize, e1[Z], e1[Y], fez, fey, min, max, rad))
        {
            return false;
        }
        if (!axis_test_y02(v0, v2, boxhalfsize, e1[Z], e1[X], fez, fex, min, max, rad))
        {
            return false;
        }
        if (!axis_test_z0(v0, v1, boxhalfsize, e1[Y], e1[X], fey, fex, min, max, rad))
        {
            return false;
        }

        fex = fabsf(e2[X]);
        fey = fabsf(e2[Y]);
        fez = fabsf(e2[Z]);

        if (!axis_test_x2(v0, v1, boxhalfsize, e2[Z], e2[Y], fez, fey, min, max, rad))
        {
            return false;
        }
        if (!axis_test_y1(v0, v1, boxhalfsize, e2[Z], e2[X], fez, fex, min, max, rad))
        {
            return false;
        }
        if (!axis_test_z12(v1, v2, boxhalfsize, e2[Y], e2[X], fey, fex, min, max, rad))
        {
            return false;
        }

        /* Bullet 1: */
        /*  first test overlap in the {x,y,z}-directions */
        /*  find min, max of the triangle each direction, and test for overlap in */
        /*  that direction -- this is equivalent to testing a minimal AABB around */
        /*  the triangle against the AABB */
        /* test in X-direction */

        find_min_max(v0[X], v1[X], v2[X], min, max);
        if (min > boxhalfsize[X] || max < -boxhalfsize[X])
        {
            return false;
        }
        /* test in Y-direction */
        find_min_max(v0[Y], v1[Y], v2[Y], min, max);
        if (min > boxhalfsize[Y] || max < -boxhalfsize[Y])
        {
            return false;
        }
        /* test in Z-direction */
        find_min_max(v0[Z], v1[Z], v2[Z], min, max);
        if (min > boxhalfsize[Z] || max < -boxhalfsize[Z])
        {
            return false;
        }

        /* Bullet 2: */
        /*  test if the box intersects the plane of the triangle */
        /*  compute plane equation of triangle: normal*x+d=0 */
        cross(normal, e0, e1);

        return static_cast<bool>(plane_box_overlap(normal, v0, boxhalfsize)); /* box and triangle overlaps */
    }

  public:
    // looks for the largest value of orig_du and copies it to the corresponding value: either du0, du1 or du2.
    static void restore_true_value_of_dx_max(declfloat& du0, declfloat& du1, declfloat& du2,
                                             const std::array<declfloat, 3>& orig_du)
    {
        auto it = std::max_element(orig_du.begin(), orig_du.end(),
                                   [](auto x, auto y)
                                   {
                                       return std::abs(x) < std::abs(y);
                                   });
        auto dist = std::distance(orig_du.begin(), it);
        switch (dist)
        {
            case 0:
                du0 = orig_du[0];
                break;
            case 1:
                du1 = orig_du[1];
                break;
            case 2:
                du2 = orig_du[2];
                break;
            default:
                throw std::logic_error("Unexpected case value");
        }
    }

    // returns true iff two trilines (colinear triangles) self intersect
    // also computes and returns: coplanarity, isectpot1, isectpt2
    static bool triline_triline_self_intersect_and_isectline(
        const TemplatedVec& V0, const TemplatedVec& EV1, const TemplatedVec& EV2,  // face 1
        const TemplatedVec& U0, const TemplatedVec& EU1, const TemplatedVec& EU2,  // face 2
        detail::Coplanarity& coplanarity,                                          // are the faces coplanar?
        TemplatedVec& isectpt2,      // 2nd endpoint of intersection segment
        TemplatedVec& isectpt1,      // 1st endpoint of intersection segment
        bool check_isect_endpoints,  // generate isectpt1 and isectpt2?
        int num_shared_vertices)
    {
        switch (num_shared_vertices)
        {
            case 0:
                return triline_triline_self_intersect_and_isectline_0(V0, EV1, EV2, U0, EU1, EU2, coplanarity, isectpt2,
                                                                      isectpt1, check_isect_endpoints);
            case 1:
                assert(V0 == U0);
                return triline_triline_self_intersect_and_isectline_1(V0, EV1, EV2, EU1, EU2, coplanarity, isectpt2,
                                                                      isectpt1);
            case 2:
                assert(V0 == U0);
                assert(EV1 == EU1);
                return triline_triline_self_intersect_and_isectline_2(V0, EV1, EV2, EU2, coplanarity, isectpt2,
                                                                      isectpt1);
            case 3:
                throw std::logic_error("duplicated triangles are not allowed");

            default:
                throw std::logic_error("internal error");
        }
    }

    // returns true iff two trilines (colinear triangles) sharing 0 vertices self-intersect
    // verifies if the trilines are colinear (coplanarity)
    // may return isectline (isectpt1, isectpt2)
    static bool triline_triline_self_intersect_and_isectline_0(
        const TemplatedVec& V0, const TemplatedVec& EV1, const TemplatedVec& EV2,  // face 1
        const TemplatedVec& U0, const TemplatedVec& EU1, const TemplatedVec& EU2,  // face 2
        detail::Coplanarity& coplanarity,                                          // are the faces coplanar?
        TemplatedVec& isectpt2,      // 2nd endpoint of intersection segment
        TemplatedVec& isectpt1,      // 1st endpoint of intersection segment
        bool check_isect_endpoints)  // generate isectpt1 and isectpt2?
    {
        TemplatedVec w = U0 - V0;
        // aa, ab, bb are coefficients of a (symmetric) system of linear equations 2x2
        // this system gives the position of the two points on two straight lines that are closest to each other
        declfloat aa = EV1.norm_squared();
        declfloat ab = -EV1.dot(EU1);
        declfloat bb = EU1.norm_squared();
        declfloat b0 = w.dot(EV1);  // b0, b1 are r.h.s of the system of linear equatins
        declfloat b1 = -w.dot(EU1);

        declfloat t, s;  // unknowns solved for
        bool solution_is_unique;

        moeller::detail::solve_spd_linear_equations(s, t, solution_is_unique, aa, ab, bb, b0, b1);

        // maximum and minimum acceptable values of s that lie within the face
        declfloat max_s = EV2.abs() / EV1.abs();
        declfloat min_s = 0.0;

        // Currently the vertices are sorted according to x-axis and then y-axis order upon being read from file.
        // This ordering makes the following "if" clause redundant.
        // However, it is possible that this ordering is not strictly preserved during healing or other
        //  mesh-modifying actions. Hence, I leave this code as is, even though currently thre's no realistic
        // way of testing its validity shoud the condition be satisfied
        // The test MoellerIntersectionTest.triline_triline_self_intersect_and_isectline_0_test
        //  is designed to brute-force cover the contents of the if
        if (EV2.dot(EV1) < 0)
        {
            min_s = -max_s;
            max_s = 0.0;
        }

        // maximum and minimum acceptable values of t that lie within the face
        declfloat max_t = EU2.abs() / EU1.abs();
        declfloat min_t = 0.0;

        // see the comment for the previous "if"
        if (EU2.dot(EU1) < 0)
        {
            min_t = -max_t;
            max_t = 0.0;
        }

        if (!solution_is_unique)  // trilines are parallel
        {
            coplanarity = detail::Coplanarity::YES;

            // find the distance between the trilines
            TemplatedVec tmp;
            cross(tmp, w, EU1);
            float distance = tmp.abs() / sqrt(bb);
            if (distance > detail::Tolerance::get_value())
            {
                return false;  // trilines are parallel but not colinear
            }

            // trilines are colinear

            TemplatedVec n{EV1};
            bool status = n.normalize();
            if (!status)
            {
                throw std::logic_error{};
            }
            // xv1, xv2. xu1, xu2 are coordinates of V1,...,U2 projected onto the triline
            // in this coordinate system, position of U0 is its origin
            declfloat xv1 = n.dot(EV1);
            declfloat xv2 = n.dot(EV2);
            declfloat xu[3] = {n.dot(U0), n.dot(U0 + EU1), n.dot(U0 + EU2)};
            if (xv2 < xv1)
            {  // make sure xv1 <= xv2
                std::swap(xv1, xv2);
            }

            std::sort(xu, xu + 3);  // by sorting, we can identify & eliminate the "central" point

            if (xu[0] > xv2 || xv1 > xu[2])
            {
                return false;
            }
            // the trilines self-intersect
            if (check_isect_endpoints)
            {
                if (xu[0] < xv2)
                {
                    isectpt1 = U0 + EU1;
                    isectpt2 = V0 + EV2;
                }
                else
                {
                    isectpt1 = U0 + EU2;
                    isectpt2 = V0 + EV1;
                }
            }
            return true;
        }

        assert(solution_is_unique);  // at this point the trilines are not parallel

        TemplatedVec delta = U0;
        if (t > max_t)
        {
            t = max_t;
        }
        if (t < min_t)
        {
            t = min_t;
        }
        if (s > max_s)
        {
            s = max_s;
        }
        if (s < min_s)
        {
            s = min_s;
        }

        delta += t * EU1;
        delta -= V0;
        delta -= s * EV1;  // Delta is the shortest vector connecting two (infinite) lines

        double distance = delta.abs();
        // If the he lines intersect...
        if (distance <= detail::Tolerance::get_value())
        {
            coplanarity = detail::Coplanarity::YES;
            if (check_isect_endpoints)
            {
                isectpt1 = U0 + t * EU1;
                isectpt2 = V0 + s * EV1;
            }
            return true;
        }

        coplanarity = detail::Coplanarity::NO;
        return false;
    }

    // returns true iff two trilines (colinear triangles) sharing 1 vertex self-intersect
    // verifies if the trilines are colinear (coplanarity)
    // may return isectline (isectpt1, isectpt2)
    static bool triline_triline_self_intersect_and_isectline_1(
        const TemplatedVec& V0, const TemplatedVec& EV1, const TemplatedVec& EV2,  // face 1
        const TemplatedVec& EU1, const TemplatedVec& EU2,                          // face 2
        detail::Coplanarity& coplanarity,                                          // are the faces coplanar?
        TemplatedVec& isectpt2,  // 2nd endpoint of intersection segment
        TemplatedVec& isectpt1)  // generate isectpt1 and isectpt2?
    {
        coplanarity = detail::Coplanarity::YES;

        bool colinear = is_wedge_colinear(EV1, EU1);
        isectpt1 = isectpt2 = V0;
        if (!colinear)
        {
            return false;
        }
        // the trilines are colinear
        TemplatedVec n = EU1;
        n.normalize();
        declfloat xu1 = dot(n, EU1);
        declfloat xu2 = dot(n, EU2);
        declfloat xv1 = dot(n, EV1);
        declfloat xv2 = dot(n, EV2);

        return xu1 * xv1 > 0 || xu1 * xv2 > 0 || xu2 * xv1 > 0 || xu2 * xv2 > 0;
    }

    // returns true iff two trilines (colinear triangles) sharing 2 vertices self-intersect
    // verifies if the trilines are colinear (coplanarity)
    // may return isectline (isectpt1, isectpt2)
    static bool triline_triline_self_intersect_and_isectline_2(
        const TemplatedVec& V0, const TemplatedVec& EV1, const TemplatedVec& EV2,  // face 1
        const TemplatedVec& EU2,                                                   // face 2
        detail::Coplanarity& coplanarity,                                          // are the faces coplanar?
        TemplatedVec& isectpt2,  // 2nd endpoint of intersection segment
        TemplatedVec& isectpt1)  // 1st endpoint of intersection segment
    {
        coplanarity = detail::Coplanarity::YES;
        isectpt1 = V0;
        isectpt2 = V0 + EV1;

        TemplatedVec n{V0};
        n.normalize();
        declfloat x0 = 0;
        declfloat x1 = dot(n, EV1);
        declfloat xv = dot(n, EV2);
        declfloat xu = dot(n, EU2);
        if (x1 < 0)
        {
            x1 = -x1;
            xv = -xv;
            xu = -xu;
        }
        if (xu < x0 && xv > x1)
        {
            return false;
        }
        if (xv < x0 && xu > x1)
        {
            return false;
        }
        return true;
    }

    void inline static conditionally_round_to_zero(declfloat& d)
    {
        if (fabs(d) < detail::Tolerance::get_value())
        {
            d = 0.0;
        }
    };

    // V0, V1, V2 are vertices of face 1
    // U0, U1, U2 are vertices of face 2
    // coplanar is passed back as true iff faces 1 and 2 are found to be coplanar
    // isectpt1, isectpt2 return endpoints of line segement shared by face 1 and 2 if they intersect
    //   and are not coplanar
    // return value: true iff faces 1 and 2 intersect
    static bool tri_tri_intersect_with_isectline(
        const TemplatedVec& V0, const TemplatedVec& V1, const TemplatedVec& V2,  // face 1
        const TemplatedVec& U0, const TemplatedVec& U1, const TemplatedVec& U2,  // face 2
        detail::Coplanarity& coplanarity,                                        // are the faces coplanar?
        TemplatedVec& isectpt2,                                                  // 2nd endpoint of intersection segment
        TemplatedVec& isectpt1,                                                  // 1st endpoint of intersection segment
        bool check_isect_endpoints,  // should we generate here isectpt1, isectpt2?
        int num_shared_vertices)
    {
        coplanarity = detail::Coplanarity::NO;

        TemplatedVec e_v1 = {0.0, 0.0, 0.0};  // first  side of face 1 (as vector)
        TemplatedVec e_v2 = {0.0, 0.0, 0.0};  // second side of face 1
        TemplatedVec e_u1 = {0.0, 0.0, 0.0};  // first  side of face 2 (as vector)
        TemplatedVec e_u2 = {0.0, 0.0, 0.0};  // second side of face 2
        TemplatedVec n1 = {0.0, 0.0, 0.0};    // normal to face 1
        TemplatedVec n2 = {0.0, 0.0, 0.0};    // normal to face 2
        declfloat d1, d2;
        declfloat du0 = 0, du1 = 0, du2, dv0 = 0, dv1 = 0, dv2;
        TemplatedVec d = {0.0, 0.0, 0.0};
        declfloat isect1[2], isect2[2];
        TemplatedVec isectpoint_a1 = {0.0, 0.0, 0.0};
        TemplatedVec isectpoint_a2 = {0.0, 0.0, 0.0};
        TemplatedVec isectpoint_b1 = {0.0, 0.0, 0.0};
        TemplatedVec isectpoint_b2 = {0.0, 0.0, 0.0};
        declfloat du0du1{0}, du0du2{0}, dv0dv1{0}, dv0dv2{0};
        declfloat vp0, vp1, vp2;
        declfloat up0, up1, up2;
        declfloat d_squared = -1.0;

        std::array<declfloat, 3> orig_du{0, 0, 0};
        std::array<declfloat, 3> orig_dv{0, 0, 0};

        declfloat const tolerance = detail::Tolerance::get_value();

        /* compute plane equation of triangle(V0,V1,V2) */
        sub(e_v1, V1, V0);                       // E1 = V1 - V0
        sub(e_v2, V2, V0);                       // E2 = V2 - V0
        n1 = guarded_cross_product(e_v1, e_v2);  // N1 = E1 \times E2
        bool n1_exists = norm(n1) > 0;
        normalize(n1);  // normalization; added by ZK
        /* compute plane of triangle (U0,U1,U2) */
        sub(e_u1, U1, U0);                       // E1 = U1 - U0
        sub(e_u2, U2, U0);                       // E2 = U2 - U0
        n2 = guarded_cross_product(e_u1, e_u2);  // N2 = E1 \times E2
        bool n2_exists = norm(n2) > 0;
        normalize(n2);  // normalization; added by ZK

        if (n1_exists && !n2_exists)
        {
            n2 = normal_to_line_and_within_plane(n1, e_u1);
        }

        if (!n1_exists && n2_exists)
        {
            n1 = normal_to_line_and_within_plane(n2, e_v1);
        }

        if (!n1_exists && !n2_exists)
        {
            throw std::logic_error("unexpected code path was hit");
        }

        d1 = -dot(n1, V0);  // d1 = -N1.V0
        /* plane equation 1: N1.X + d1 = 0 */

        /* put U0, U1, U2 into plane equation 1 to compute signed distances to the plane */

        if (num_shared_vertices == 0)
        {                            //
            du0 = dot(n1, U0) + d1;  // distance of U0 to face (V0, V1, V2)
        }
        if (num_shared_vertices < 2)
        {                            //
            du1 = dot(n1, U1) + d1;  // distance of U1 to face (V0, V1, V2)
        }
        du2 = dot(n1, U2) + d1;  // distance of U2 to face (V0, V1, V2)

        orig_du[0] = du0;
        orig_du[1] = du1;
        orig_du[2] = du2;

        // In the instructions below, du0, du1 and du2 may be conditionally/artifically set to 0
        // This does not seem to influence any arithmetic computations (vertex coordinates are left intact)
        // However, their value equal to zero is used further below in conditional statements
        //   to indicate that a vertex from a face is coplanar with the other face
        //   and this bit of information is used as a branch selector in the algorithmic tree
        // Thus, the value of eff_tolerance controls the definition of 4 vertices being considered "coplanar"
        conditionally_round_to_zero(du0);  // if (fabs(du0) < tolerance) du0 = 0.0;
        conditionally_round_to_zero(du1);  // if (fabs(du1) < tolerance) du1 = 0.0;
        conditionally_round_to_zero(du2);  // if (fabs(du2) < tolerance) du2 = 0.0;

        /* D = N1 \times N2 is orthogonal both to N1 and N2, unless both triangles are coplanar
         * Therefore, D shows the direction of the intersection line, which is orthogonal to both N1 and N2
         * Moreover, D cannot be a zero vector here, for the case of N1 parallel to N2 has already been processed
         *  in one of the return statements above
         */
        cross(d, n1, n2);

        // The magnitude of the cross product of two normalized vectors is the sine of the angle between them
        // Thus, D_squared is the sine of the angle between N1 and N2, squared
        d_squared = d[0] * d[0] + d[1] * d[1] + d[2] * d[2];

        if (du0 == 0 && du1 == 0 && du2 == 0)
        {
            if (d_squared < COPLANARITY_THRESHOLD_SQUARED * 100.0f || !n1_exists || !n2_exists)
            {
                coplanarity = detail::Coplanarity::YES;
                return coplanar_tri_tri(n1, n1, U0, U1, U2, V0, V1, V2);  // RETURN
            }

            restore_true_value_of_dx_max(du0, du1, du2, orig_du);
        }

        du0du1 = du0 * du1;
        du0du2 = du0 * du2;

        d2 = -dot(n2, U0);  // d2 = -N2.U0
        /* plane equation 2: N2.X+d2=0 */

        /* put V0,V1,V2 into plane equation 2 */
        if (num_shared_vertices == 0)
        {  //
            dv0 = dot(n2, V0) + d2;
        }
        if (num_shared_vertices < 2)
        {  //
            dv1 = dot(n2, V1) + d2;
        }
        dv2 = dot(n2, V2) + d2;

        orig_dv[0] = dv0;
        orig_dv[1] = dv1;
        orig_dv[2] = dv2;

        conditionally_round_to_zero(dv0);  // if (fabs(dv0) < tolerance) dv0 = 0.0;
        conditionally_round_to_zero(dv1);  // if (fabs(dv1) < tolerance) dv1 = 0.0;
        conditionally_round_to_zero(dv2);  // if (fabs(dv2) < tolerance) dv2 = 0.0;

        if (dv0 == 0 && dv1 == 0 && dv2 == 0)
        {
            if (d_squared < COPLANARITY_THRESHOLD_SQUARED * 100.0f || !n1_exists || !n2_exists)
            {
                coplanarity = detail::Coplanarity::YES;
                return coplanar_tri_tri(n2, n2, V0, V1, V2, U0, U1, U2);  // RETURN
            }

            restore_true_value_of_dx_max(dv0, dv1, dv2, orig_dv);
        }

        dv0dv1 = dv0 * dv1;
        dv0dv2 = dv0 * dv2;

        /* if U0, U1, U2 are on the same side of face (V0, V1, V2) even if their coordinates are known +- epsilon/2
         */
        if (num_shared_vertices == 0)
        {
            if (du0du1 > 0 && du0du2 > 0)
            {
                return false; /* RETURN: no intersection occurs */
            }
            if (dv0dv1 > 0 && dv0dv2 > 0)
            {
                return false; /* RETURN: no intersection occurs */
            }
        }
        else if (num_shared_vertices == 1)
        {
            if (du1 * du2 > 0 && dv1 * dv2 > 0)
            {
                set(isectpt1, U0);
                set(isectpt2, U0);
                coplanarity = detail::Coplanarity::NO;
                return true;
            }
        }
        else
        {
            if (du2 != 0 && dv2 != 0)
            {
                set(isectpt1, U0);
                set(isectpt2, U1);
                coplanarity = detail::Coplanarity::NO;
                return true;
            }
        }

        if (num_shared_vertices == 2)  // the triangles intersect only at the two shared vertices
        {
            if (check_isect_endpoints)
            {
                set(isectpt1, V0);
                set(isectpt2, V1);
            }
            return true;
        }

        if (d_squared < COPLANARITY_THRESHOLD_SQUARED)
        {
            // The angle between the two triangle surfaces is very small
            // and each of them intersects the other triangle's plane, so we can assume the're effectively coplanar
            return coplanar_tri_tri(n1, n2, V0, V1, V2, U0, U1, U2);
        }

        if (d_squared < INTERSECTION_TEST_THRESHOLD_SQUARED)
        {
            coplanarity = detail::Coplanarity::MAYBE;
        }
        /*
         * At this point we know that the faces are not coplanar
         */

        // the test below is quite reliable in rejecting self-intersections
        if (num_shared_vertices == 0 && d_squared < INTERSECTION_TEST_THRESHOLD_SQUARED)
        {
            bool b = coplanar_tri_tri(n1, n2, V0, V1, V2, U0, U1, U2);
            if (!b)
            {
                return false;
            }
        }

        /* compute the index into the largest component of D */

        unsigned index = index_into_largest_component_abs(d);

        /* Projection onto the axis corresponding to index */
        /* This corresponds to projection onto x, y, or z, whichever is "closer" to the direction of isectline D */
        vp0 = V0[index];
        vp1 = V1[index];
        vp2 = V2[index];

        up0 = U0[index];
        up1 = U1[index];
        up2 = U2[index];

        /* compute interval for triangle 1 */
        compute_intervals_isectline(V0, V1, V2, vp0, vp1, vp2, dv0, dv1, dv2, dv0dv1, dv0dv2, isect1[0], isect1[1],
                                    isectpoint_a1, isectpoint_a2, orig_dv, num_shared_vertices);

        /* compute interval for triangle 2 */
        compute_intervals_isectline(U0, U1, U2, up0, up1, up2, du0, du1, du2, du0du1, du0du2, isect2[0], isect2[1],
                                    isectpoint_b1, isectpoint_b2, orig_du, num_shared_vertices);

        /* !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! */
        /* !!!!!!!  at this point we know that the triangles are not coplanar  !!!!!!! */
        /* !!!!!!!  and we have the triangle-with-plain intersection points    !!!!!!! */
        /* !!!!!!!  if any                                                     !!!!!!! */
        /* !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! */

        // test for not overlapping of two line segments
        if (isect1[1] < isect2[0] - tolerance || isect2[1] < isect1[0] - tolerance)  // tolerance added by ZK
        {
            return false;  // RETURN
        }

        /* !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! */
        /* !!!!!!!  at this point we know that the triangles intersect  !!!!!!!!! */
        /* !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! */

        if (!check_isect_endpoints)
        {
            return true;  // RETURN
        }

        if (isect1[0] == isect1[1])
        {
            set(isectpt1, isectpoint_a1);
            set(isectpt2, isectpoint_a1);
            return true;
        }
        if (isect2[0] == isect2[1])
        {
            set(isectpt1, isectpoint_b1);
            set(isectpt2, isectpoint_b1);
            return true;
        }
        if (isect2[0] < isect1[0])
        {
            set(isectpt1, isectpoint_a1);
            if (isect2[1] < isect1[1])
            {
                set(isectpt2, isectpoint_b2);
            }
            else
            {
                set(isectpt2, isectpoint_a2);
            }
        }
        else
        {
            set(isectpt1, isectpoint_b1);
            if (isect2[1] > isect1[1])
            {
                set(isectpt2, isectpoint_a2);
            }
            else
            {
                set(isectpt2, isectpoint_b2);
            }
        }
        return true;
    }

    // N is a vector orthogonal to the plane defined by V0, V1, and V2.
    //
    static bool coplanar_tri_tri(const TemplatedVec& N1, const TemplatedVec& N2, const TemplatedVec& V0,
                                 const TemplatedVec& V1, const TemplatedVec& V2, const TemplatedVec& U0,
                                 const TemplatedVec& U1, const TemplatedVec& U2)
    {
        TemplatedVec a{0.0, 0.0, 0.0};
        size_t i0, i1;
        /* first project onto an axis-aligned plane, that maximizes the area */
        /* of the triangles, compute indices: i0, i1. */
        a[X] = fabs(N1[X]) + fabs(N2[X]);
        a[Y] = fabs(N1[Y]) + fabs(N2[Y]);
        a[Z] = fabs(N1[Z]) + fabs(N2[Z]);
        if (a[X] > a[Y])
        {
            if (a[X] > a[Z])
            {
                i0 = 1; /* A[X] is greatest, so exclude X==0 from i0, i1 */
                i1 = 2;
            }
            else
            {
                i0 = 0; /* A[Z] is greatest, so exclude Z==2 from i0, i1 */
                i1 = 1;
            }
        }
        else /* A[X]<=A[Y] */
        {
            if (a[Z] > a[Y])
            {
                i0 = 0; /* A[Z] is greatest, so exclude Z==2 from i0, i1 */
                i1 = 1;
            }
            else
            {
                i0 = 0; /* A[Y] is greatest, so exclude Y==1 from i0, i1  */
                i1 = 2;
            }
        }

        /* test all edges of triangle 1 against the edges of triangle 2 */
        if (edge_against_tri_edge(V0, V1, U0, U1, U2, i0, i1))
        {
            return true;
        }
        if (edge_against_tri_edge(V1, V2, U0, U1, U2, i0, i1))
        {
            return true;
        }
        if (edge_against_tri_edge(V2, V0, U0, U1, U2, i0, i1))
        {
            return true;
        }

        /* finally, test if tri1 is totally contained in tri2 or vice versa */
        if (point_in_tri(V0, U0, U1, U2, i0, i1))
        {
            return true;
        }
        if (point_in_tri(U0, V0, V1, V2, i0, i1))
        {
            return true;
        }

        return false;
    }

  private:
    // Computes intersection line.
    // Returns true iff succeeds.
    inline static void compute_intervals_isectline(
        const TemplatedVec& VERT0,        // vertex 0 of the reference triangle
        const TemplatedVec& VERT1,        // vertex 1
        const TemplatedVec& VERT2,        // vertex 2
        const declfloat VV0,              // projection of VERT0 on a "safe" axis (x, y, or z)
        const declfloat VV1,              // -,,-          VERT1  -,,-
        const declfloat VV2,              // -,,-          VERT2  -,,-
        const declfloat D0,               // signed distance of U0 from the reference triangle's plane
        const declfloat D1,               // -,,-               U1
        const declfloat D2,               // -,,-               U2
        const declfloat D0D1,             // D0 * D1
        const declfloat D0D2,             // D0 * D2
        declfloat& isect0,                // endpoint 0 of intersection line segment on the projection axis
        declfloat& isect1,                // endpoint 1 of intersection line segment on the projection axis
        TemplatedVec& isectpoint0,        // endpoint 0 of intersection line segment in 3D
        TemplatedVec& isectpoint1,        // endpoint 1 of intersection line segment in 3D
        std::array<declfloat, 3> orig_D,  //
        int num_shared_vertices)
    {
        // If the conditions were not satisfied, the triangles would certainly not intersect or be coplanar,
        // which must have been detected earlier
        assert(D0 <= 0 || D1 <= 0 || D2 <= 0);
        assert(D0 >= 0 || D1 >= 0 || D2 >= 0);
        assert(D0 != 0 || D1 != 0 || D2 != 0);  // traingles cannot be coplanar

        assert(D0D1 == D0 * D1);
        assert(D0D2 == D0 * D2);

        assert(num_shared_vertices < 2 && num_shared_vertices >= 0);

        // The table below helps me understand the flow of the function logic.
        // Here +, 0, - mean >0, =0, <0
        //  thus, three consecutive +s, 0s, or -s correspond to the sign of D0, D1, D2, resp.
        // A number that follows represents the "case", see the compound if...elseif... below
        // The three numbers in square brackests indicate the oder of arguments to isect2, see below
        // So: "++- 0 [201]" means: the case D0 > 0, D1 > 0, D2 < 0 is handled in CASE 0 with argument order: 2,0,1
        //
        //  +++  impossible by contract
        //  ++0  0  [201]
        //  ++-  0  [201]
        //  +0+  1  [102]
        //  +00  2' [012]
        //  +0-  2' [012]
        //  +-+  1  [102]
        //  +-0  2' [012]
        //  +--  2  [012]
        //  0++  2  [012]
        //  0+0  3  [102]
        //  0+-  3  [102]
        //  00+  4  [201]
        //  000  5  coplanar, impossible by contract (here throwing exception, in orig. Moeller's impl. returns "true")
        //  00-  4  [201]
        //  0-+  3  [102]
        //  0-0  3  [102]
        //  0--  2  [012]
        //  -++  2  [012]
        //  -+0  2' [012]
        //  -+-  1  [102]
        //  -0+  2' [012]
        //  -00  2' [012]
        //  -0-  1  [102]
        //  --+  0  [201]
        //  --0  0  [201]
        //  ---  impossible by contract

        if (D0D1 > 0.0)  // CASE 0 [201]: ++0 or ++- or --0 or --+
        {
            /* here we know that D0 > 0, D1 > 0, D2 <= 0.0, which is written ++0 or ++- */
            /* that is D0, D1 are on the same side, D2 on the other or on the reference plane */
            assert(D0 * D2 <= 0);
            isect2(VERT2, VERT0, VERT1, VV2, VV0, VV1, orig_D[2], orig_D[0], orig_D[1], isect0, isect1, isectpoint0,
                   isectpoint1);
        }
        else if (D0D2 > 0.0f)  // CASE 1 [102]: +0+ or +-+ or -0- or -+-
        {
            /* here we know that d0d1 <= 0.0 */
            assert(D0 * D1 <= 0);
            isect2(VERT1, VERT0, VERT2, VV1, VV0, VV2, orig_D[1], orig_D[0], orig_D[2], isect0, isect1, isectpoint0,
                   isectpoint1);
        }
        else if (D1 * D2 > 0.0f || D0 != 0.0f)  // CASE 2 [012]:
        {
            if (num_shared_vertices == 0)
            {
                isect2(VERT0, VERT1, VERT2, VV0, VV1, VV2, orig_D[0], orig_D[1], orig_D[2], isect0, isect1, isectpoint0,
                       isectpoint1);
            }
            else
            {
                isect2_shared_at_v0(VERT0, VV0, isect0, isect1, isectpoint0, isectpoint1);
            }
        }
        else if (D1 != 0.0f)  // CASE 3: [102] 0-+ or 0-0 or 0+0 or 0+-
        {
            if (num_shared_vertices == 0)
            {
                isect2(VERT1, VERT0, VERT2, VV1, VV0, VV2, orig_D[1], orig_D[0], orig_D[2], isect0, isect1, isectpoint0,
                       isectpoint1);
            }
            else
            {
                assert(orig_D[0] == 0);
                isect2_shared_at_v1(VERT1, VERT0, VERT2, VV1, VV0, VV2, orig_D[1], orig_D[2], isect0, isect1,
                                    isectpoint0, isectpoint1);
            }
        }
        else if (D2 != 0.0f)  // CASE 4 [201]: 00+ or 00-
        {
            if (num_shared_vertices == 0)
            {
                isect2(VERT2, VERT0, VERT1, VV2, VV0, VV1, orig_D[2], orig_D[0], orig_D[1], isect0, isect1, isectpoint0,
                       isectpoint1);
            }
            else
            {
                assert(orig_D[0] == 0);
                isect2_shared_at_v1(VERT2, VERT0, VERT1, VV2, VV0, VV1, orig_D[2], orig_D[1], isect0, isect1,
                                    isectpoint0, isectpoint1);
            }
        }
        else  // CASE 5: 000 [coplanar]
        {
            throw std::logic_error{
                "triangles are coplanar (!?). This is an ERROR, as this case should have been dealt with by the "
                "caller"};
        }
    }
};
}  // namespace moeller
}  // namespace threeyd

#endif  // THREEYD_MOELLER_TRIANGLEINTERSECTS_HPP
