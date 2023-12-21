import json
import os
import sys
import time
import operator
import itertools
import functools

from collections import defaultdict
from functools import reduce
from dataclasses import dataclass, field

try:
    import igraph as graph

    has_igraph = True
except:
    import networkx as graph
    print("Warning: networkx uses considerable amounts of memory consider install igraph")

    has_igraph = False

import numpy
from scipy.spatial import KDTree

import voxec
import ifcopenshell
import ifcopenshell.geom

from ifcopenshell.util.unit import calculate_unit_scale

import utils


@dataclass
class model_geometry:
    """
    Stores the extracted geometric detail for a certain set of elements, including the arbitrarily precise plain equations and their correspondence to polyhedral facets.
    """
    # list[pair[int, int]]
    #            ^ convex_halfspace_trees[...]
    #                 ^ convex_halfspace_trees[n][...]
    epeck_equation_idxs: list = field(default_factory=list)

    # list[pair[str, tuple[plane]]]
    convex_halfspace_trees: list = field(default_factory=list)

    # list[list[plane]]
    non_convex_halfspace_facets_equations: list = field(default_factory=list)
    float_facet_normals: list = field(default_factory=list)
    float_facet_centroids: list = field(default_factory=list)

    def __add__(self, other):
        """Concatenate two model_geometry objects

        Args:
            other (model_geometry): Other set of interpreted geometries

        Returns:
            _type_: model_geometry
        """
        l = len(self.convex_halfspace_trees)
        return model_geometry(
            self.epeck_equation_idxs + [(i + l, j) for i, j in other.epeck_equation_idxs],
            self.convex_halfspace_trees + other.convex_halfspace_trees,
            self.non_convex_halfspace_facets_equations + other.non_convex_halfspace_facets_equations,
            self.float_facet_normals + other.float_facet_normals,
            self.float_facet_centroids + other.float_facet_centroids,
        )

class context:
    
    def __init__(self, fn):
        self.fn = fn
        self.bfn = os.path.basename(fn)
        self.is_substituted = False
        substituted_fn = self.bfn + ".substituted.ifc"

        if os.path.exists(substituted_fn):
            self.is_substituted = True
            self.f = ifcopenshell.open(substituted_fn)
        else:
            self.f = ifcopenshell.open(fn)

        self.elems = self.prefilter_elements_using_voxelization(exclude=('IfcOpeningElement', 'IfcSpace'))

        if not self.is_substituted:
            self.f, self.orig_f = self.substitute_detailed_elements(include=self.elems), self.f
            self.f.write(substituted_fn)

        self.opening_elems = list(itertools.chain.from_iterable([rel.RelatedOpeningElement for rel in getattr(el, "HasOpenings", ())] for el in self.elems))
        openings = self.extract_geometry(include=self.opening_elems)
        data = self.extract_geometry(include=self.elems)

        all_geom = openings + data

        my_mapping = self.create_mapping(all_geom)

        self.apply_mapping(all_geom, my_mapping)

        del my_mapping

        new_data = utils.make_default(self.apply_openings(data, openings))

        del data
        del openings

        result = self.union(itertools.chain.from_iterable(new_data.values()))

        with open(self.bfn + ".obj", "w") as ff:
            ff.write(result.serialize_obj())

    def substitute_with_box(self, file, elem, min_thickness=0.01):
        """
        Computes a (somewhat) optimal oriented bounding box around the triangulated geometry described in elem by constructing a local reference frame based on the prevalent triangle normals

        Args:
            file (ifcopenshell.file): file containing elem
            elem (TriangulationElement): triangulated geometry 
            min_thickness (float, optional): minimal thickness of the oriented bounding box to create around elem

        Returns:
            tuple: <guid, <3x4 matrix, min, max>> with min and max being the local coords in the matrix
        """
        vs = numpy.array(elem.geometry.verts).reshape((-1, 3))
        fs = numpy.array(elem.geometry.faces).reshape((-1, 3))

        def _():
            for f in fs:
                p, q, r = vs[f]
                pq = q - p
                pr = r - p
                pq /= numpy.linalg.norm(pq)
                pr /= numpy.linalg.norm(pr)
                pqr = numpy.cross(pq, pr)
                pqr /= numpy.linalg.norm(pqr)
                yield pqr

        tri_norms = numpy.array(list(_()))
        _, inv, cnts = numpy.unique(numpy.int_(tri_norms * 1000), return_counts=True, return_inverse=True, axis=0)
        di = utils.make_default(sorted((j, i) for i, j in enumerate(inv)))
        V = numpy.average(tri_norms[di[numpy.argsort(cnts)[-1]]], axis=0)
        candidates = []
        for i in range(1, min(10, len(cnts))):
            ref = numpy.average(tri_norms[di[numpy.argsort(cnts)[-i]]], axis=0)
            candidates.append((abs(ref @ V), ref))
        if not candidates:
            refs = [(0, 0, 1), (1, 0, 0)]
            for ref in refs:
                candidates.append((abs(ref @ V), ref))
        ref = min(candidates, key=operator.itemgetter(0))[1]
        Y = numpy.cross(V, ref)
        X = numpy.cross(V, Y)
        M = numpy.array((X, -Y, V))

        Mi = numpy.linalg.inv(M)
        vsi = numpy.array([Mi @ v for v in vs])

        vsimi = vsi.min(axis=0)
        vsima = vsi.max(axis=0)

        for i in range(3):
            d = vsima[i] - vsimi[i]
            if d < min_thickness:
                dd = (min_thickness - d) / 2.0
                vsima[i] += dd
                vsimi[i] -= dd

        vsimi = vsimi / calculate_unit_scale(file)
        vsima = vsima / calculate_unit_scale(file)

        return (elem.id,) + tuple(x.tolist() for x in (M.T, vsimi, vsima))

    @utils.trace
    def prefilter_elements_using_voxelization(self, **kwargs):
        """Uses a course voxelization (5cm) to quickly detect the likely subset
        of elements participating in the building exterior. In case of small cavities
        protruding into the building, bounding elements may be omitted from the
        return list of elements.

        Returns:
            list[ifcopenshell.entity_instance]
        """
        if os.path.exists(self.bfn + ".elements.json"):
            return [self.f[i] for i in json.load(open(self.bfn + ".elements.json"))]
        result = []

        s = ifcopenshell.geom.settings(
            USE_WORLD_COORDS=True,
            WELD_VERTICES=False,
            DISABLE_OPENING_SUBTRACTIONS=True,
            ITERATOR_OUTPUT=ifcopenshell.ifcopenshell_wrapper.SERIALIZED,
        )

        building_elements_union = None
        building_elements = []

        it = ifcopenshell.geom.iterator(s, self.f, geometry_library="opencascade", **kwargs)

        if not it.initialize():
            # print(ifcopenshell.get_log())
            # exit(1)
            return result

        while True:
            elem = it.get()
            geom = elem.geometry.brep_data
            if self.f[int(elem.geometry.id.split("-")[0])].RepresentationIdentifier != "Box":
                # breakpoint()
                vox = voxec.run("voxelize", geom, method="volume")
                building_elements.append((self.f[elem.id], vox))
                if building_elements_union is None:
                    building_elements_union = vox
                else:
                    building_elements_union = building_elements_union.boolean_union(vox)
            if not it.next():
                break

        exterior = voxec.run("exterior", building_elements_union)
        exterior_shell = [voxec.run("offset", exterior)]
        for i in range(1):
            exterior_shell.append(voxec.run("offset", exterior_shell[-1]))
        exterior_shell_thick = reduce(lambda a, b: a.boolean_union(b), exterior_shell)

        for elem, vox in building_elements:
            if exterior_shell_thick.boolean_intersection(vox).count():
                result.append(elem)

        json.dump([i.id() for i in result], open(self.bfn + ".elements.json", "w"))
        return result

    def substitute_detailed_elements(self, force=False, **kwargs):
        """Substitute elements with a high vertex count with an
        oriented bounding box.

        Args:
            force (bool, optional): Substitute regardless of vertex count. Defaults to False.

        Returns:
            ifcopenshell.file: file with substitutions made to the representation items
        """
        s = ifcopenshell.geom.settings(
            USE_WORLD_COORDS=True,
            # ITERATOR_OUTPUT=ifcopenshell.ifcopenshell_wrapper.NATIVE,
            ITERATOR_OUTPUT=ifcopenshell.ifcopenshell_wrapper.TRIANGULATED,
            DISABLE_OPENING_SUBTRACTIONS=True,
        )
        it = ifcopenshell.geom.iterator(s, f, geometry_library="cgal", **kwargs)
        if not it.initialize():
            return

        substitutions = []
        while True:
            nat = it.get_native()
            elem = it.get()
            num_verts = len(elem.geometry.verts) // 3
            volume = sum(nat.geometry.item(i).volume().to_double() for i in range(nat.geometry.size()))
            if force or num_verts > 128 or (num_verts / volume) > 2000:
                substitutions.append(self.substitute_with_box(f, elem))
            if not it.next():
                break

        f = self.f
        for elid, m3, mi, ma in substitutions:
            elem = f[elid]
            elem.ObjectPlacement = f.createIfcLocalPlacement(
                RelativePlacement=f.createIfcAxis2Placement3D(
                    f.createIfcCartesianPoint((0.0, 0.0, 0.0)),
                    f.createIfcDirection(m3[2]),
                    f.createIfcDirection(m3[0]),
                )
            )

            rep = [rep for rep in elem.Representation.Representations if rep.RepresentationIdentifier == "Body"][0]
            elem.Representation = f.createIfcProductDefinitionShape(
                None,
                None,
                [
                    f.createIfcShapeRepresentation(
                        rep[0],
                        rep[1],
                        "SweptSolid",
                        Items=[
                            f.createIfcExtrudedAreaSolid(
                                f.createIfcRectangleProfileDef(
                                    "AREA",
                                    None,
                                    f.createIfcAxis2Placement2D(f.createIfcCartesianPoint(((ma[0] - mi[0]) / 2.0, (ma[1] - mi[1]) / 2.0))),
                                    ma[0] - mi[0],
                                    ma[1] - mi[1],
                                ),
                                f.createIfcAxis2Placement3D(f.createIfcCartesianPoint(mi)),
                                f.createIfcDirection((0.0, 0.0, 1.0)),
                                ma[2] - mi[2],
                            )
                        ],
                    )
                ],
            )
        return f

    @utils.trace
    def extract_geometry(self, **kwargs):
        # not only align facets part of the (potentially concave) input polyhedron, but also align facets resulting from the convex decomposition
        ALIGN_INNER = True

        s = ifcopenshell.geom.settings(
            USE_WORLD_COORDS=True,
            # ITERATOR_OUTPUT=ifcopenshell.ifcopenshell_wrapper.NATIVE,
            ITERATOR_OUTPUT=ifcopenshell.ifcopenshell_wrapper.TRIANGULATED,
            DISABLE_OPENING_SUBTRACTIONS=True,
        )

        it = ifcopenshell.geom.iterator(s, self.f, geometry_library="cgal", **kwargs)
        its = []

        data = model_geometry()

        if not it.initialize():
            # print(ifcopenshell.get_log())
            # exit(1)
            return data

        while True:
            elem = it.get()
            if self.f[int(elem.geometry.id.split("-")[0])].RepresentationIdentifier != "Box":
                print(f"[{utils.get_mem()} MB]", "reading", self.f[elem.id])

                elem = it.get_native()
                for i in range(elem.geometry.size()):
                    elem_i = elem.geometry.item(i)

                    if elem_i.num_vertices() < 6:
                        # try and detect single faces used sometime for glass panes which can't
                        # be represented as halfspace intersection and need to be 'solidified'
                        fs = elem_i.facets()
                        axes = list(utils.to_tuple(f.axis()) for f in fs)
                        if all(ax == axes[0] for ax in axes):
                            ff = ifcopenshell.file(schema=self.f.schema)
                            ff.add(*self.f.by_type("IfcProject"))
                            nelem = ff.add(self.f[elem.id])
                            body = [rep for rep in nelem.Representation.Representations if rep.RepresentationIdentifier == "Body"][0]
                            while body.Items[0].is_a("IfcMappedItem"):
                                body = body.Items[0].MappingSource.MappedRepresentation
                            body.Items = [body.Items[i]]
                            self.substitute_detailed_elements(ff, force=True)
                            ff.write("temp.ifc")
                            fff = ifcopenshell.open("temp.ifc")
                            its.append(ifcopenshell.geom.iterator(s, fff, geometry_library="cgal"))
                            assert its[-1].initialize()
                            elem2 = its[-1].get_native()
                            elem_i = elem2.geometry.item(0)

                    if ALIGN_INNER:
                        try:
                            parts = elem_i.convex_decomposition()
                        except:
                            # @todo likely due to self-intersections
                            parts = []
                    else:
                        parts = [elem_i]

                    for poly in parts:
                        cd = poly.convex_decomposition()
                        for p in cd:
                            # print('part volume', p.volume().to_double())
                            # print('part area  ', p.area().to_double())
                            pass

                        fs = poly.facets()

                        phfs = poly.halfspaces().facets()

                        if len(phfs) == 0:
                            # @todo investigate why two cases of 0-length checks needed
                            continue

                        data.non_convex_halfspace_facets_equations.append(list(map(lambda f: f.plane_equation(), phfs)))

                        ns = [f.axis() for f in fs]
                        ps_ = [f.position() for f in fs]
                        # without this weird results on linux
                        ps = [tuple(ifcopenshell.ifcopenshell_wrapper.create_epeck(x.to_string()) for x in utils.to_tuple(t)) for t in ps_]

                        ds = list(map(utils.dot, ns, ps))
                        nsd = numpy.array(list(map(utils.to_double, ns)))

                        if nsd.size == 0:
                            continue

                        nsd /= numpy.linalg.norm(nsd, axis=1).reshape((-1, 1))
                        data.float_facet_normals.append(nsd)
                        data.float_facet_centroids.append(numpy.array(list(map(utils.to_double, ps))))

                        last_hs_tups = tuple(
                            map(
                                lambda x: tuple(x.get(i) for i in range(4)),
                                data.non_convex_halfspace_facets_equations[-1],
                            )
                        )

                        data.convex_halfspace_trees.append((self.f[elem.id], tuple(p.halfspaces() for p in cd)))

                        # correlate halfspace planes back to polyhedral facets
                        for d, n1, n2 in zip(ds, ns, nsd.tolist()):
                            abcd = tuple(-n1.get(i) for i in range(3)) + (d,)

                            # @todo unable to find probably due to triangulation?
                            # ...   yes it seems that triangulation has solved this (but only to a large extent)
                            # @todo should we divide by largest component?

                            try:
                                j = last_hs_tups.index(abcd)
                            except:
                                # breakpoint()
                                enumerated_plane_eq_diff = lambda t: reduce(
                                    operator.add,
                                    ((abcd[i] - t[1][i]) * (abcd[i] - t[1][i]) for i in range(4)),
                                ).to_double()
                                if (
                                    min(
                                        map(
                                            enumerated_plane_eq_diff,
                                            enumerate(last_hs_tups),
                                        )
                                    )
                                    > 0.1
                                ):
                                    print(">", *(x.to_double() for x in abcd))
                                    for h in last_hs_tups:
                                        print(*(x.to_double() for x in h))

                                    breakpoint()
                                j = min(enumerate(last_hs_tups), key=enumerated_plane_eq_diff)[0]
                            data.epeck_equation_idxs.append((len(data.non_convex_halfspace_facets_equations) - 1, j))

            if not it.next():
                break

        return data

    @utils.trace
    def create_mapping(self, data):
        """Finds groups of halfspace plane equations that are within a certain
        angular and linear deviation, computes the average and construct a
        mapping from original to cluster average.
        """
        mapping = []

        # First use a kd-tree to find planes with similar normals (the first three) components
        # of the plane equations. Note that we search also for the opposite.

        # A single float64 vector might be associated to multiple distinct epeck equations.
        # in our kd-tree we store unique float64 coordinates and maintain a mapping back to
        # indices into the original epeck equations.
        vecs = numpy.concatenate(data.float_facet_normals)
        vecs_unique, vecs_inverse = numpy.unique(vecs, return_inverse=True, axis=0)
        vecs_dict = utils.make_default(sorted((j, i) for i, j in enumerate(vecs_inverse)))

        points = numpy.concatenate(data.float_facet_centroids)
        kdtree = KDTree(vecs_unique)

        G = graph.Graph()

        if has_igraph:
            # @todo write a proper adaptor. igraph only supports integer vertex ids, so we
            # need a separate mapping
            vertices = [(+1, i) for i in range(len(vecs_unique))] + [(-1, i) for i in range(len(vecs_unique))]
            G.add_vertices(len(vertices))
            vidx = lambda x: x[1] if x[0] == +1 else x[1] + len(vecs_unique)
            getv = lambda x: vertices[x]
            add_edges = lambda g, es: g.add_edges(es)
            components = lambda g: list(g.connected_components())
        else:
            vidx = lambda x: x
            getv = lambda x: x
            add_edges = lambda g, es: g.add_edges_from(es)
            components = lambda g: list(graph.connected_components(g))

        def yield_edges():
            for i, p in enumerate(vecs_unique):
                # @todo if i in G.nodes: continue?
                for sign in (+1, -1):
                    yield from ((vidx((+1, i)), vidx((sign, j))) for j in kdtree.query_ball_point(p * sign, r=0.01))

        add_edges(G, yield_edges())

        for comp in components(G):
            print(f"[{utils.get_mem()} MB]", "component size", len(comp))

            comp = list(map(getv, comp))

            # construct the average plane normal (keeping in mind the sign)
            # to within the component create a sorted sequence based on the dot
            # product with the polyhedral facet centroid

            # @todo should be weighted based on vecs_count?
            idx_pos = sorted(i for s, i in comp if s == +1)
            idx_neg = sorted(i for s, i in comp if s == -1)
            avgv = numpy.average(numpy.concatenate((vecs_unique[idx_pos], -vecs_unique[idx_neg])), axis=0)
            avgv /= numpy.linalg.norm(avgv)

            def augment(c):
                for s, i in c:
                    for j in vecs_dict[i]:
                        yield s, j

            comp = list(augment(comp))

            idx_both = [i for s, i in comp]
            # the original facet centroids
            pts = points[idx_both]
            ds = pts @ avgv
            shuff = numpy.argsort(pts @ avgv)
            srted = ds[shuff]
            diff = numpy.diff(srted)

            # cluster based on jumps in sorted array
            chunks = numpy.split(shuff, numpy.where(diff > 0.002)[0] + 1)

            for chunk in chunks:
                comp_subset = [comp[c] for c in chunk]

                Gcomp = graph.Graph()
                if has_igraph:
                    Gcomp_vs = dict(map(reversed, enumerate(comp_subset)))
                    Gcomp.add_vertices(len(comp_subset))
                    Gcomp_vidx = lambda x: Gcomp_vs[x]
                    Gcomp_getv = lambda x: comp_subset[x]
                else:
                    Gcomp_vidx = lambda x: x
                    Gcomp_getv = lambda x: x

                def _():
                    # Project facet centroid onto plane both sides and compare
                    for (sa, a), (sb, b) in itertools.combinations(comp_subset, 2):
                        d = abs((points[b] - points[a]) @ vecs[a]) + abs((points[a] - points[b]) @ vecs[b])
                        if d < 0.001:
                            yield Gcomp_vidx((sa, a)), Gcomp_vidx((sb, b))

                # This becomes the final connected component of plane equations to be averaged
                add_edges(Gcomp, _())

                for comp2 in components(Gcomp):
                    comp2 = list(map(Gcomp_getv, comp2))
                    eqt = []
                    idxs = set()
                    for sign in (+1, -1):
                        # eqids = sum((double_to_orig[V] for V in set(map(tuple, vecs[[c for s, c in comp2 if s == sign]].tolist()))), [])
                        eqids = [data.epeck_equation_idxs[c] for s, c in comp2 if s == sign]
                        eqs = [data.non_convex_halfspace_facets_equations[a][b] for a, b in eqids]
                        idxs.update(a for a, b in eqids)
                        # tuples
                        for a in map(utils.negate(sign), map(utils.to_tuple, eqs)):
                            if a not in eqt:
                                eqt.append(a)

                    N = ifcopenshell.ifcopenshell_wrapper.create_epeck(len(eqt))
                    # transpose
                    eqtt = list(zip(*eqt))
                    # sum and divide components
                    avg = utils.to_opaque(
                        list(
                            map(
                                functools.partial(utils.reserialize, to_double=False),
                                [reduce(operator.add, comps) / N for comps in eqtt],
                            )
                        )
                    )
                    for pl in map(utils.to_opaque, eqt):
                        mapping.append((pl, avg, idxs))
        return mapping

    @utils.trace
    def apply_mapping(self, data, mapping):
        by_id = defaultdict(lambda: (list(), list()))
        for a, b, idxs in mapping:
            for idx in idxs:
                by_id[idx][0].append(a)
                by_id[idx][1].append(b)

        for i, (elem, ps) in enumerate(data.convex_halfspace_trees):
            for p in ps:
                p.map(*by_id[i])

    @utils.trace
    def evaluate(self, data):
        def inner():
            for elem, ps in data.convex_halfspace_trees:
                print("Evaluating", elem)
                solids = [p.solid() for p in ps]
                # @todo use union()
                v = solids[0]
                for p in solids[1:]:
                    v = v.add(p)

                yield elem, v

        return list(inner())

    @utils.trace
    def apply_openings(self, data, openings):
        def inner():
            opgeom = utils.make_default(self.evaluate(openings))
            for k, v in self.evaluate(data):
                for el in getattr(k, "HasOpenings", ()):
                    print("opening", k, el.RelatedOpeningElement)
                    for p in opgeom[el.RelatedOpeningElement]:
                        v = v.subtract(p)
                        # print('v.volume', v.volume().to_double())
                yield k, v

        return list(inner())

    @staticmethod
    @utils.trace
    def union(shapes):
        return ifcopenshell.ifcopenshell_wrapper.nary_union(list(shapes))

if __name__ == "__main__":      
    fn = sys.argv[1]
    context(fn)
