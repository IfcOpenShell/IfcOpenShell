import argparse
import json
import math
import os
import sys
import time
import operator
import itertools
import functools
import threading
            
import concurrent.futures
import multiprocessing

from collections import defaultdict
from functools import reduce
from dataclasses import dataclass, field, fields

try:
    import igraph as graph

    has_igraph = True
except:
    import networkx as graph
    print("Warning: networkx uses considerable amounts of memory consider install igraph")

    has_igraph = False

import numpy
from scipy.spatial import KDTree
from scipy.spatial import ConvexHull

import voxec
import ifcopenshell
import ifcopenshell.geom

from ifcopenshell.util.unit import calculate_unit_scale

import utils

# numpy.seterr(all='raise')

to_str = lambda eq: tuple(x.to_string() for x in utils.to_tuple(eq))

@dataclass
class settings:
    debug : bool = False
    verbose : bool = False
    resolution : float = 1.e-5
    voxel_prefiltering : bool = True
    detailed_element_substitution : bool = True
    element_categories : list = None
    element_guids : list = None
    store_mapping : bool = False
    existing_mapping : bool = False


@dataclass
class model_geometry:
    """
    Stores the extracted geometric detail for a certain set of elements, including the arbitrarily precise plain equations and their correspondence to polyhedral facets.
    """
    # list[list[int]]
    #            ~^ non_convex_halfspace_facets_equations[...]~
    #                 ^ non_convex_halfspace_facets_equations[n][...]
    # 
    # used to map after finding clusters on plane equations
    # float_facet_normals[i] -> non_convex_halfspace_facets_equations[i][j]
    epeck_equation_idxs: list = field(default_factory=list)

    # list[pair[str, tuple[halfspacetree]]]
    # used to apply mapping to
    convex_halfspace_trees: list = field(default_factory=list)

    # halfspaces > facets > plane_equation
    # list[list[plane]]
    non_convex_halfspace_facets_equations: list = field(default_factory=list)
    # normalized list[ndarray[N, 3]]
    float_facet_normals: list = field(default_factory=list)
    # list[ndarray[N, 3]]
    float_facet_centroids: list = field(default_factory=list)

    def __add__(self, other):
        """Concatenate two model_geometry objects

        Args:
            other (model_geometry): Other set of interpreted geometries

        Returns:
            _type_: model_geometry
        """
        return model_geometry(
            self.epeck_equation_idxs + other.epeck_equation_idxs,
            self.convex_halfspace_trees + other.convex_halfspace_trees,
            self.non_convex_halfspace_facets_equations + other.non_convex_halfspace_facets_equations,
            self.float_facet_normals + other.float_facet_normals,
            self.float_facet_centroids + other.float_facet_centroids,
        )

class context:
    
    def __init__(self, fns : list, output : str, st : settings):
        self.fns = fns
        self.is_substituted = False
        self.settings = st
        self.fs = []

        if self.settings.detailed_element_substitution:
            for fn in fns:
                bfn = os.path.basename(fn)
                substituted_fn = bfn + ".substituted.ifc"

                if os.path.exists(substituted_fn):
                    self.is_substituted = True
                    self.fs.append(ifcopenshell.open(substituted_fn))
                else:
                    self.fs.append(ifcopenshell.open(fn))

        if self.settings.voxel_prefiltering:
            if self.settings.element_categories:
                self.elems = self.prefilter_elements_using_voxelization(exclude=('IfcOpeningElement', 'IfcSpace'))
            else:
                self.elems = self.prefilter_elements_using_voxelization(include=self.settings.element_categories)
        elif self.settings.element_categories:
            self.elems = reduce(operator.add, itertools.chain.from_iterable((map(f.by_type, self.settings.element_categories) for f in self.fs)))
        elif self.settings.element_guids:
            def wrap_try(fn, default = None):
                def inner():
                    try:
                        return fn()
                    except:
                        return default
                return inner
            self.elems = sum((list(map(wrap_try(f.by_guid), self.settings.element_guids)) for f in self.fs), [])
        else:
            self.elems = [inst for f in self.fs for inst in f.by_type('IfcProduct') if not inst.is_a('IfcOpeningElement') or inst.is_a('IfcSpace')]

        if not self.is_substituted and self.settings.detailed_element_substitution:
            substituted_files = []
            for fn, f in zip(self.fns, self.fs):
                bfn = os.path.basename(fn)
                substituted_fn = bfn + ".substituted.ifc"
                substituted_files.append((self.substitute_detailed_elements(f, include=self.elems), f))
                substituted_files[-1][0].write(substituted_fn)
            self.fs, self.orig_files = zip(*substituted_files)

        self.opening_elems = list(itertools.chain.from_iterable([rel.RelatedOpeningElement for rel in getattr(el, "HasOpenings", ())] for el in self.elems))
        openings = self.extract_geometry(include=self.opening_elems)
        data = self.extract_geometry(include=self.elems)

        openings = self.remove_narrow(openings)
        data = self.remove_narrow(data)

        all_geom = openings + data

        if self.settings.existing_mapping:
            my_mapping = json.load(open('epeck_mapping.json'))
            def deser(strs):
                return tuple(utils.to_opaque(tuple(map(utils.create_epeck, st.split(' ')))) for st in strs)
            my_mapping = {k: list(map(list, zip(*map(deser, vs)))) for k, vs in my_mapping.items() if k in map(operator.attrgetter('GlobalId'), self.elems)}
        else:
            my_mapping = self.create_mapping(all_geom)
        
        self.apply_mapping(all_geom, my_mapping, from_disk=self.settings.existing_mapping)

        del my_mapping

        new_data = utils.make_default(self.apply_openings(data, openings))

        del data
        del openings

        result = self.union(itertools.chain.from_iterable(new_data.values()))

        with open(output, "w") as ff:
            ff.write(result.serialize_obj())


    @staticmethod
    def definition_is_convex(repitem):
        if repitem.is_a('IfcExtrudedAreaSolid'):
            if repitem.SweptArea.is_a('IfcRectangleProfileDef'):
                return True
            if repitem.SweptArea.is_a() == 'IfcArbitraryClosedProfileDef':
                crv = repitem.SweptArea.OuterCurve
                if crv.is_a('IfcPolyline'):
                    points = numpy.array([p.Coordinates for p in crv.Points])[:-1, :]
                elif crv.is_a('IfcIndexedPolyCurve'):
                    points = numpy.array(crv.Points.CoordList)
                    if crv.Segments:
                        if any(seg.is_a('IfcArcIndex') for seg in crv.Segments):
                            return False
                        idxs = numpy.array(seg[0][0] for seg in crv.Segments) - 1
                        points = points[idxs]
                    else:
                        # ?
                        points = points[:, :-1]
                else:
                    return False
                
                return len(ConvexHull(points[:, 0:2]).vertices) == len(points)

    def substitute_with_box(self, file, elem, min_thickness=0.01, force=False):
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

        def _():
            for f in fs:
                p, q, r = vs[f]
                pq = q - p
                pr = r - p
                pqr = numpy.cross(pq, pr)
                yield numpy.linalg.norm(pqr) / 2.

        tri_areas = numpy.array(list(_()))

        _, inv, cnts = numpy.unique(numpy.int_(tri_norms * 1000), return_counts=True, return_inverse=True, axis=0)
        di = utils.make_default(sorted((j, i) for i, j in enumerate(inv)))
        summed_area = [v[1] for v in sorted((k, sum(tri_areas[v])) for k, v in di.items())]
        sorted_summed_areas = numpy.argsort(summed_area)
        V = numpy.average(tri_norms[di[sorted_summed_areas[-1]]], axis=0)
        candidates = []
        for i in range(1, min(10, len(cnts))):
            ref = numpy.average(tri_norms[di[sorted_summed_areas[-i]]], axis=0)
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
        vsi = numpy.array([v @ Mi for v in vs])

        vsimi = vsi.min(axis=0)
        vsima = vsi.max(axis=0)

        for i in range(3):
            d = vsima[i] - vsimi[i]
            if d < min_thickness:
                dd = (min_thickness - d) / 2.0
                vsima[i] += dd
                vsimi[i] -= dd

        def norm(v):
            return v / numpy.linalg.norm(v)
        
        def approx_diff():
            for tri in vsi[fs]:
                e1, e2 = tri[1:] - tri[0]
                c = numpy.cross(e1, e2)
                a = numpy.linalg.norm(c) / 2.
                n = norm(c)
                cent = numpy.average(tri, axis=0)
                def distances():
                    for bnd in (vsimi, vsima):
                        for v in numpy.diag(cent - bnd):
                            if numpy.linalg.norm(v) < 1.e-9:
                                yield numpy.inf, 0.
                            else:
                                yield norm(v) @ n, numpy.linalg.norm(v)
                yield max(distances())[1] * a

        if not force: 
            bbox_dim = functools.reduce(operator.mul, vsima - vsimi)
            approx_volume_diff = sum(approx_diff())
            volume_factor = approx_volume_diff / bbox_dim
            if volume_factor >= 0.25:
                return None

        vsimi = vsimi / calculate_unit_scale(file)
        vsima = vsima / calculate_unit_scale(file)

        return (elem.id,) + tuple(x.tolist() for x in (M, vsimi, vsima))

    @utils.trace
    def prefilter_elements_using_voxelization(self, **kwargs):
        """Uses a course voxelization (5cm) to quickly detect the likely subset
        of elements participating in the building exterior. In case of small cavities
        protruding into the building, bounding elements may be omitted from the
        return list of elements.

        Returns:
            list[ifcopenshell.entity_instance]
        """
        if all(os.path.exists(bfn + ".elements.json") for bfn in map(os.path.basename, self.fns)):
            return sum(([f[i] for i in json.load(open(bfn + ".elements.json"))] for f, bfn in zip(self.fs, map(os.path.basename, self.fns))), [])
        
        results = []

        s = ifcopenshell.geom.settings(
            USE_WORLD_COORDS=True,
            WELD_VERTICES=False,
            DISABLE_OPENING_SUBTRACTIONS=True,
            ITERATOR_OUTPUT=ifcopenshell.ifcopenshell_wrapper.SERIALIZED,
        )

        building_elements_union = None
        building_elements = []

        for bfn, f in zip(map(os.path.basename, self.fns), self.fs):
            result = []
            it = ifcopenshell.geom.iterator(s, f, geometry_library="opencascade", **kwargs)

            if not it.initialize():
                # print(ifcopenshell.get_log())
                # exit(1)
                return result

            while True:
                elem = it.get()
                geom = elem.geometry.brep_data
                if f[int(elem.geometry.id.split("-")[0])].RepresentationIdentifier != "Box":
                    # breakpoint()
                    vox = voxec.run("voxelize", geom, method="volume")
                    building_elements.append((f[elem.id], vox))
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

            json.dump([i.id() for i in result], open(bfn + ".elements.json", "w"))
            results.extend(result)
        return results

    def substitute_detailed_elements(self, file=None, force=False, **kwargs):
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
        it = ifcopenshell.geom.iterator(s, file, geometry_library="cgal", **kwargs)
        if not it.initialize():
            return

        substitutions = []
        while True:
            nat = it.get_native()
            elem = it.get()
            num_verts = len(elem.geometry.verts) // 3
            num_faces = len(elem.geometry.faces) // 3
            volume = sum(nat.geometry.item(i).volume().to_double() for i in range(nat.geometry.size()))
            if force or num_verts > 128 or ((num_verts / volume) > 2000 and num_faces > 12):
                subs_result = self.substitute_with_box(f, elem, force=force)
                if subs_result:
                    substitutions.append(subs_result)
            if not it.next():
                break

        f = file
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
    # @profile
    def extract_geometry(self, **kwargs):
        # not only align facets part of the (potentially concave) input polyhedron, but also align facets resulting from the convex decomposition
        ALIGN_INNER = True

        s = ifcopenshell.geom.settings(
            USE_WORLD_COORDS=False,
            # ITERATOR_OUTPUT=ifcopenshell.ifcopenshell_wrapper.NATIVE,
            ITERATOR_OUTPUT=ifcopenshell.ifcopenshell_wrapper.TRIANGULATED,
            DISABLE_OPENING_SUBTRACTIONS=True,
        )


        its = []
        fffs = []

        data = model_geometry()


        for f in self.fs:
            if kwargs.keys() == {'include'}:
                kwargs2 = {'include': [e for e in kwargs['include'] if e.wrapped_data.file == f]}
            else:
                kwargs2 = kwargs
            it = ifcopenshell.geom.iterator(s, f, geometry_library="cgal", **kwargs2)
            
            if not it.initialize():
                # print(ifcopenshell.get_log())
                # exit(1)
                continue
            
            # convex decomposition is expensive, geometries can be shared, apply product-level transformations after CD and cache results pre-transform
            cd_cache = {}

            while True:
                elem = it.get()
                elem_g_id = elem.geometry.id
                  

                if f[int(elem_g_id.split("-")[0])].RepresentationIdentifier != "Box":
                    print(f"[{utils.get_mem()} MB]", "reading", f[elem.id])

                    elem = it.get_native()
                    elem2 = None
                    for i in range(elem.geometry.size()):
                        elem_i = elem.geometry.item(i)
                        repitem = f[elem.geometry.item_id(i)]

                        if elem_i.num_vertices() < 6:
                            # try and detect single faces used sometime for glass panes which can't
                            # be represented as halfspace intersection and need to be 'solidified'
                            fs = elem_i.facets()
                            axes_ = [f.axis() for f in fs]
                            axes = list(map(utils.to_tuple, axes_))
                            if all(ax == axes[0] for ax in axes):
                                ff = ifcopenshell.file(schema=f.schema)
                                ff.add(*f.by_type("IfcProject"))
                                nelem = ff.add(f[elem.id])
                                body = [rep for rep in nelem.Representation.Representations if rep.RepresentationIdentifier == "Body"][0]
                                while body.Items[0].is_a("IfcMappedItem"):
                                    body = body.Items[0].MappingSource.MappedRepresentation
                                body.Items = [body.Items[i]]
                                ff.write("temp.ifc")
                                fff = ifcopenshell.open("temp.ifc")
                                fffs.append(fff)
                                its.append(ifcopenshell.geom.iterator(s, fff, geometry_library="cgal"))
                                assert its[-1].initialize()
                                elem2 = its[-1].get_native()
                                elem_i = elem2.geometry.item(0)
                                repitem = body.Items[0]
                                assert not its[-1].next()

                        if ALIGN_INNER:
                            ke = elem_g_id, elem.geometry.item_id(i)
                            parts = cd_cache.get(ke)

                            if parts is None:
                                # @todo reuse decomp on shape instances                            
                                
                                if self.definition_is_convex(repitem):
                                    # convex decomposition is expensive, figure out the 
                                    # convexity from a 2d extrusion basis where possible
                                    parts = [elem_i]
                                    parts[0].convex_tag(True)
                                else:
                                    try:
                                        parts = elem_i.convex_decomposition()
                                    except:
                                        # @todo likely due to self-intersections
                                        parts = []
                                cd_cache[ke] = parts
                        else:
                            parts = [elem_i]

                        parts = [p.moved((elem2 if elem2 else elem).transformation.matrix) for p in parts]

                        for poly in parts:
                            if ALIGN_INNER:
                                cd = [poly]
                            else:
                                cd = poly.convex_decomposition()

                            for p in cd:
                                # print('part volume', p.volume().to_double())
                                # print('part area  ', p.area().to_double())
                                pass

                            assert len(cd) == 1

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
                            data.epeck_equation_idxs.append([])

                            last_hs_tups = tuple(
                                map(
                                    lambda x: tuple(x.get(i) for i in range(4)),
                                    data.non_convex_halfspace_facets_equations[-1],
                                )
                            )

                            data.convex_halfspace_trees.append((f[elem.id], tuple(p.halfspaces() for p in cd)))

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
                                data.epeck_equation_idxs[-1].append(j)

                if not it.next():
                    break

        return data

    @utils.trace
    def remove_narrow(self, data):
        negate = lambda x: utils.to_opaque(utils.negate(-1)(x))
        
        astuple_nocopy = lambda dc: list(map(functools.partial(getattr, dc), map(operator.attrgetter('name'), fields(dc))))
        datas = [model_geometry(*map(lambda x: [x], xs)) for xs in zip(*astuple_nocopy(data))]
        by_elem_id = lambda i_d: i_d[1].convex_halfspace_trees[0][0].id()
        
        datas2 = [(k, list(vs)) for k, vs in itertools.groupby(sorted(enumerate(datas), key=by_elem_id), key=by_elem_id)]

        to_remove = []

        for i, rest in datas2:
            decomps = list(map(lambda d_i: d_i[1].convex_halfspace_trees[0][1], rest))
            orig_ids = list(map(lambda d_i: d_i[0], rest))
            # only tested on align inner
            assert all(len(parts) == 1 for parts in decomps)

            internal_mapping = []
            
            for j, parts in zip(orig_ids, decomps):

                hs = parts[0]
                epecks = [h.plane_equation() for h in hs.facets()]

                # print('I', original_index)
                # for eq in epecks:
                #     print('eq', *(x.to_string() for x in utils.to_tuple(eq)))

                rounded_negated = [tuple(-int(round(v * 10000)) for v in utils.to_double(eq)) for eq in epecks]
                # for v in rounded_negated:
                #     print('ap', *v)
                
                for eq in epecks:
                    try:
                        abcd_idx = rounded_negated.index(tuple(int(round(v * 10000)) for v in utils.to_double(eq)))
                    except ValueError as e:
                        continue
                    
                    internal_mapping.append((eq, negate(epecks[abcd_idx])))
                    internal_mapping.append((negate(eq), epecks[abcd_idx]))
                    to_remove.append(j)

                    # print('removing', original_index)
                    break
            
            for j, parts in zip(orig_ids, decomps):

                if j in to_remove:
                    continue
                    
                hs = parts[0]
                for ab in internal_mapping:
                    hs.map(*ab)

        datas_filtered = [d for i, d in enumerate(datas) if i not in to_remove]
        if not datas_filtered:
            return model_geometry()
        else:
            return reduce(operator.add, datas_filtered)

    @utils.trace
    def create_mapping(self, data):
        """Finds groups of halfspace plane equations that are within a certain
        angular and linear deviation, computes the average and construct a
        mapping from original to cluster average.
        """

        if self.settings.verbose and self.settings.debug:
            for ii, eqs in enumerate(data.non_convex_halfspace_facets_equations):
                print('ELEMENT', ii)
                for i, eq in enumerate(eqs):
                    print(i, *to_str(eq))

        epeck_equation_list_idx = numpy.cumsum([0] + list(map(len, data.epeck_equation_idxs)))
        # epeck_equation_idxs_flat = list(itertools.chain.from_iterable(data.epeck_equation_idxs))

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
            # vertices = [(+1, i) for i in range(len(vecs_unique))] + [(-1, i) for i in range(len(vecs_unique))]
            G.add_vertices(len(vecs_unique))
            vidx = lambda x: x
            getv = lambda x: x
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
                    yield from ((i,j) for j in kdtree.query_ball_point(p * sign, r=0.2))
            # for i in range(len(vecs_unique)):
            #     yield (vidx((+1, i)), vidx((-1, i)))

        add_edges(G, yield_edges())

        for comp in components(G):
            print(f"[{utils.get_mem()} MB]", "component size", len(comp))

            comp = list(map(getv, comp))

            # construct the average plane normal (keeping in mind the sign)
            # to within the component create a sorted sequence based on the dot
            # product with the polyhedral facet centroid

            # @todo should be weighted based on vecs_count?
            # idx_pos = sorted(i for s, i in comp if s == +1)
            # idx_neg = sorted(i for s, i in comp if s == -1)

            signs = numpy.sign(vecs_unique[comp] @ vecs_unique[comp][0]).reshape((-1,1))
            avgv = numpy.average(vecs_unique[comp] * signs, axis=0)
            avgv /= numpy.linalg.norm(avgv)

            def augment(c):
                for i in c:
                    for j in vecs_dict[i]:
                        yield j

            comp = list(augment(comp))

            # the original facet centroids
            pts = points[comp]
            ds = pts @ avgv
            shuff = numpy.argsort(pts @ avgv)
            srted = ds[shuff]
            diff = numpy.diff(srted)

            # cluster based on jumps in sorted array
            chunks = numpy.split(shuff, numpy.where(diff > 2 * self.settings.resolution)[0] + 1)

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
                    for a, b in itertools.combinations(comp_subset, 2):
                        d = abs((points[b] - points[a]) @ vecs[a]) + abs((points[a] - points[b]) @ vecs[b])
                        if d < self.settings.resolution:
                            yield Gcomp_vidx(a), Gcomp_vidx(b)

                # This becomes the final connected component of plane equations to be averaged
                add_edges(Gcomp, _())

                for comp2 in components(Gcomp):
                    comp2 = list(map(Gcomp_getv, comp2))

                    signs = list(map(int, numpy.sign(vecs[comp2] @ vecs[comp2][0])))

                    eqt = []
                    idxs = set()

                    listidxs = [numpy.searchsorted(epeck_equation_list_idx, c, side='right')-1 for c in comp2]
                    modelo = [(j - epeck_equation_list_idx[i]) for i, j in zip(listidxs, comp2)]
                    eqs = [data.non_convex_halfspace_facets_equations[a][data.epeck_equation_idxs[a][b]] for a, b in zip(listidxs, modelo)]
                    idxs.update(listidxs)
                    # tuples
                    for a in map(lambda sign, tup: utils.negate(sign)(tup), signs, map(utils.to_tuple, eqs)):
                        if a not in eqt:
                            eqt.append(a)

                    N = ifcopenshell.ifcopenshell_wrapper.create_epeck(len(eqt))
                    # transpose
                    eqtt = list(zip(*eqt))
                    # sum and divide components
                    avg = tuple(
                        map(
                            functools.partial(utils.reserialize, to_double=False),
                            [reduce(operator.add, comps) / N for comps in eqtt],
                        )
                    )
                    avgs = tuple(map(lambda s: utils.to_opaque(utils.negate(s)(avg)), (+1, -1)))
                    for sign, pl in zip(signs, eqs):
                        mapping.append((pl, avgs[sign == -1], idxs))
        return mapping

    @utils.trace
    def apply_mapping(self, data, mapping, from_disk=False):
        if from_disk:
            by_id = mapping
        else:
            by_id = defaultdict(lambda: (list(), list()))
            for a, b, idxs in mapping:
                fr, to = (" ".join(map(lambda n: n.to_string(), utils.to_tuple(x))) for x in (a,b))
                if fr == to:
                    continue
                for idx in idxs:
                    by_id[idx][0].append(a)
                    by_id[idx][1].append(b)

            if self.settings.store_mapping:
                # can be used to store global mapping and apply to individually extracted elements
                mapping = defaultdict(list)
                for k, vs in by_id.items():
                    guid = data.convex_halfspace_trees[k][0].GlobalId
                    for ab in zip(*vs):
                        from_to = tuple(" ".join(map(lambda n: n.to_string(), utils.to_tuple(x))) for x in ab)
                        mapping[guid].append(from_to)
                json.dump(mapping, open('epeck_mapping.json', 'w'))

        for i, (elem, ps) in enumerate(data.convex_halfspace_trees):

            if from_disk:
                maps = by_id[elem.GlobalId]
            else:
                maps = by_id[i]

            for j, p in enumerate(ps):
                    
                if self.settings.verbose:
                    pps = p.solid()
                    old_area = pps.area().to_double()
                    old_volume = pps.volume().to_double()
                    open(f'{i}_{j}_before.obj', 'w').write(pps.serialize_obj())

                p.map(*maps)

                if self.settings.verbose:
                    for ab in zip(*maps):
                        c, d = map(utils.to_double, ab)
                        print(*c, '->', *d)
                        c, d = map(to_str, ab)
                        print(*c, '->', *d)

                    pps = p.solid()
                    new_area = pps.area().to_double()
                    new_volume = pps.volume().to_double()
                    open(f'{i}_{j}_after.obj', 'w').write(pps.serialize_obj())
                    if new_area:
                        print(i, j, new_area / old_area, old_area, new_area, old_volume, new_volume)

                        if new_area / old_area > 100:
                            breakpoint()

    @staticmethod
    def write_obj(ofn, *, elem=None, item=None):
        s = ifcopenshell.geom.settings(USE_WORLD_COORDS=True, WELD_VERTICES=False)
        if item:
            geom = item.Triangulate(s)
        else:
            geom = elem.geometry

        vs_fs = geom.verts, geom.faces
        vs, fs = map(lambda tup: numpy.array(tup).reshape((-1, 3)), vs_fs)

        with open(ofn, "w") as obj:
            for v in vs:
                print('v', *v, file=obj)
            for f in fs + 1:
                print('f', *f, file=obj)

    @utils.trace
    def evaluate_st(self, data):
        def inner():
            for i, (elem, ps) in enumerate(data.convex_halfspace_trees):
                print("Evaluating", elem)
                solids = [p.solid() for p in ps]
                # @todo use union()

                if len(solids) == 0:
                    continue
                elif len(solids) == 1:
                    v = solids[0]
                else:
                    v = ifcopenshell.ifcopenshell_wrapper.nary_union(solids)

                if self.settings.debug:
                    self.write_obj(f"{elem.GlobalId}_{i}.obj", item=v)

                yield elem, v

        return list(inner())

    def evaluate_mt(self, data):
        def ev(i_elem_ps):
            i, (elem, ps) = i_elem_ps
            v = ps[0].solid_mt()
            if self.settings.debug:
                self.write_obj(f"{elem.GlobalId}_{i}.obj", item=v)
            return (elem, v)
        # yield from map(ev, data.convex_halfspace_trees)
        # return
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            # futures = (executor.submit(ev, el) for el in data.convex_halfspace_trees)
            # yield from map(lambda f: f.result(), concurrent.futures.as_completed(futures))
            return executor.map(ev, enumerate(data.convex_halfspace_trees))


    @utils.trace
    def apply_openings(self, data, openings):
        def inner():
            opgeom = utils.make_default(self.evaluate_mt(openings))
            for k, v in self.evaluate_mt(data):
                for el in getattr(k, "HasOpenings", ()):
                    print("opening", k, el.RelatedOpeningElement)
                    for p in opgeom[el.RelatedOpeningElement]:
                        v = v.subtract(p)
                        # print('v.volume', v.volume().to_double())
                yield k, v

        return list(inner())

    @staticmethod
    @utils.trace
    def union_mt(shapes):
        shps = list(shapes)
        n = int(math.ceil(len(shps) / 4))
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            # futures = (executor.submit(ev, el) for el in data.convex_halfspace_trees)
            # yield from map(lambda f: f.result(), concurrent.futures.as_completed(futures))
            return ifcopenshell.ifcopenshell_wrapper.nary_union(list(executor.map(ifcopenshell.ifcopenshell_wrapper.nary_union, (shps[i*n:i*n+n] for i in range(4)))))

    @staticmethod
    @utils.trace
    def union(shapes):
        return ifcopenshell.ifcopenshell_wrapper.nary_union(list(shapes))


if __name__ == "__main__": 
    parser = argparse.ArgumentParser()
    parser.add_argument("files", type=str, nargs="+")

    for field in fields(settings):
        if field.type == bool:
            parser.add_argument("--" + field.name.replace("_", "-"), dest=field.name, action="store_true")
            parser.add_argument("--no-" + field.name.replace("_", "-"), dest=field.name, action="store_false")
            parser.set_defaults(**{field.name: field.default})
        else:
            if field.type is list:
                parser.add_argument(
                    "--" + field.name.replace("_", "-"), dest=field.name, type=lambda s: s.split(','), default=field.default
                )
            else:
                parser.add_argument(
                    "--" + field.name.replace("_", "-"), dest=field.name, type=field.type, default=field.default
                )

    args = vars(parser.parse_args(sys.argv))
    files = args.pop("files")
    if os.path.basename(__file__) == os.path.basename(files[0]):
        files = files[1:]
    output = files.pop()
    assert files

    settings = settings(**args)
    context(files, output, settings)

