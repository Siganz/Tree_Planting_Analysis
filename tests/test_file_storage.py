import stp.storrage.file_storage as fs


def test_sanitize_layer_name():
    assert fs.sanitize_layer_name("bad name!") == "bad_name_"


def test_get_geopackage_path(tmp_path):
    gpkg = fs.get_geopackage_path(tmp_path)
    assert gpkg.parent == tmp_path
