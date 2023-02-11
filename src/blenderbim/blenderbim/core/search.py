def show_scene_elements(spatial):
    spatial.show_scene_objects()

def search(search, spatial, query, action):
    products = search.from_selector_query(query)
    spatial.deselect_objects()
    try:
        spatial.filter_products(products, action)
    except:
        return "One or More Products could not be found because they are hidden in the ViewLayer"