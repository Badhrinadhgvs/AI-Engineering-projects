from .summ_test import (
    run_denver,
    run_10,
    run_afrikaans1,
    run_albanian1,
    run_arabic102,
)


def test_summ1():
    assert run_denver() != None


def test_summ2():
    assert run_10() != None


def test_summ3():
    assert run_afrikaans1() != None


def test_summ4():
    assert run_albanian1() != None


def test_summ5():
    assert run_arabic102() != None
