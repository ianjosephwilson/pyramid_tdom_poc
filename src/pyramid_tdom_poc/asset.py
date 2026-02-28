from pyramid.response import FileResponse
from pyramid.httpexceptions import HTTPNotFound
from importlib.resources import files, as_file


ALLOWED_ASSETS = frozenset(["tachyons.css", "red.png"])


def assets_view(request):
    # @NOTE: This should usually be behind some sort of static proxy.
    asset_name = request.matchdict["asset_name"]
    if asset_name in ALLOWED_ASSETS:
        source = files(__package__).joinpath("assets").joinpath(asset_name)
    else:
        raise HTTPNotFound()
    # @TODO: This is gross but just trying out this API...
    with as_file(source) as source_path:
        return FileResponse(source_path, request=request)


def includeme(config):
    config.add_route("assets", "/assets/{asset_name}")
    config.add_view(assets_view, route_name="assets")
