from src.convert_utils import get_target_extension


def test_get_target_extension_supported():
    assert get_target_extension(".doc") == ".docx"
    assert get_target_extension(".DOC") == ".docx"
    assert get_target_extension(".ppt") == ".pptx"
    assert get_target_extension(".PPT") == ".pptx"
    assert get_target_extension(".xls") == ".xlsx"
    assert get_target_extension(".XLS") == ".xlsx"


def test_get_target_extension_unsupported():
    assert get_target_extension(".xyz") is None
    assert get_target_extension(".XYZ") is None
