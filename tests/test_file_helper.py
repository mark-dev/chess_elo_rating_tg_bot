import file_helper


def test_file_helper():
    assert file_helper.is_file_size_ok(1024, limit_in_mb=5)
    assert not file_helper.is_file_size_ok(10485760, limit_in_mb=5)
