from unittest import TestCase

from eddington_core import (
    FitFunctionLoadError,
    fit_function,
    FitFunctionsRegistry,
    fit_function_generator,
)


class TestFitFunctionRegistryAddAndRemove(TestCase):
    def setUp(self):
        self.backup = frozenset(FitFunctionsRegistry.all())
        self.func1 = self.dummy_function(1)
        self.func2 = self.dummy_function(2)
        self.func3 = self.dummy_function(3)
        self.func4 = self.dummy_function(4, save=False)

        self.generator1 = self.dummy_function_generator(1)

        self.funcs = [self.func1, self.func2, self.func3, self.generator1]

    def tearDown(self):
        FitFunctionsRegistry.clear()
        for func in self.backup:
            FitFunctionsRegistry.add(func)

    @classmethod
    def dummy_function(cls, value, save=True):
        @fit_function(
            n=2,
            name=f"dummy_function{value}",
            syntax=f"syntax_dummy_function{value}",
            save=save,
        )
        def dummy_func(a, x):
            return value

        return dummy_func

    @classmethod
    def dummy_function_generator(cls, value, save=True):
        @fit_function_generator(
            parameters="p",
            name=f"dummy_generator{value}",
            syntax=f"syntax_dummy_generator{value}",
        )
        def dummy_generator(param):
            @fit_function(
                n=2,
                name=f"generated_dummy_function{param}_value{value}",
                syntax=f"syntax_generated_dummy_function{param}_value{value}",
                save=save,
            )
            def dummy_func(a, x):
                return param * value

            return dummy_func

        return dummy_generator

    def test_get_function(self):
        actual_func = FitFunctionsRegistry.get(self.func1.name)
        self.assertEqual(
            self.func1,
            actual_func,
            msg="Registry get function returns different function than expected.",
        )

    def test_get_function_generator(self):
        actual_generator = FitFunctionsRegistry.get(self.generator1.name)
        self.assertEqual(
            self.generator1,
            actual_generator,
            msg="Registry get function returns different generator than expected.",
        )

    def test_load_function(self):
        actual_func = FitFunctionsRegistry.load(self.func1.name)
        self.assertEqual(
            self.func1,
            actual_func,
            msg="Registry get name function returns different function than expected.",
        )

    def test_load_generator(self):
        actual_func = FitFunctionsRegistry.load(self.generator1.name, 2)
        self.assertEqual(
            "generated_dummy_function2_value1",
            actual_func.name,
            msg="Returned function is different than expected",
        )

    def test_exists(self):
        for func in self.funcs:
            self.assertTrue(
                FitFunctionsRegistry.exists(func.name),
                msg=f"Expected {func.name} to exists. It does not.",
            )

    def test_remove(self):
        FitFunctionsRegistry.remove(self.func1.name)
        self.assertFalse(
            FitFunctionsRegistry.exists(self.func1.name),
            msg=f"Expected {self.func1.name} to not exist. It does.",
        )

    def test_all(self):
        self.assertEqual(
            self.funcs,
            list(FitFunctionsRegistry.all()),
            msg="Functions are different than expected",
        )

    def test_names(self):
        self.assertEqual(
            [func.name for func in self.funcs],
            list(FitFunctionsRegistry.names()),
            msg="Functions names are different than expected",
        )

    def test_syntax_of_one_function(self):
        syntax = FitFunctionsRegistry.syntax([self.func1.name])
        expected_string = """
+-----------------+------------------------+
|     Function    |         Syntax         |
+-----------------+------------------------+
| dummy_function1 | syntax_dummy_function1 |
+-----------------+------------------------+"""
        self.assertEqual(
            expected_string[1:],
            str(syntax),
            msg="Syntax of one function is different than expected.",
        )

    def test_syntax_of_two_functions(self):
        syntax = FitFunctionsRegistry.syntax([self.func1.name, self.func3.name])
        expected_string = """
+-----------------+------------------------+
|     Function    |         Syntax         |
+-----------------+------------------------+
| dummy_function1 | syntax_dummy_function1 |
| dummy_function3 | syntax_dummy_function3 |
+-----------------+------------------------+"""
        self.assertEqual(
            expected_string[1:],
            str(syntax),
            msg="Syntax of two functions is different than expected.",
        )

    def test_list(self):
        syntax = FitFunctionsRegistry.list()
        expected_string = """
+---------------------+-------------------------+
|       Function      |          Syntax         |
+---------------------+-------------------------+
|   dummy_function1   |  syntax_dummy_function1 |
|   dummy_function2   |  syntax_dummy_function2 |
|   dummy_function3   |  syntax_dummy_function3 |
| dummy_generator1(p) | syntax_dummy_generator1 |
+---------------------+-------------------------+"""
        self.assertEqual(
            expected_string[1:],
            str(syntax),
            msg="Syntax of two functions is different than expected.",
        )

    def test_add_dummy_function_without_saving(self):
        self.assertFalse(
            FitFunctionsRegistry.exists(self.func4.name),
            msg="Function was saved, even though it wasn't supposed to",
        )

    def test_get_non_existing_function(self):
        self.assertRaisesRegex(
            FitFunctionLoadError,
            f"^No fit function or generator named {self.func4.name}$",
            FitFunctionsRegistry.get,
            self.func4.name,
        )

    def test_load_non_existing_function(self):
        self.assertRaisesRegex(
            FitFunctionLoadError,
            f"^No fit function or generator named {self.func4.name}$",
            FitFunctionsRegistry.load,
            self.func4.name,
        )

    def test_load_fit_function_with_parameters(self):
        self.assertRaisesRegex(
            FitFunctionLoadError,
            f"^{self.func1.name} is not a generator and should not get parameters$",
            FitFunctionsRegistry.load,
            self.func1.name,
            1,
            2,
        )