import ecc_rankings.run

def test_import_run():
    assert hasattr(ecc_rankings, "run")
    assert callable(ecc_rankings.run.main)


def test_run_main_executes():
    # This just checks that main() runs without error (does not validate output)
    try:
        ecc_rankings.run.main()
    except Exception as e:
        assert False, f"ecc_rankings.run.main() raised an exception: {e}"

