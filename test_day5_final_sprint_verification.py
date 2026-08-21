# test_day5_final_sprint_verification.py
# Master Test Suite for Day 5 Final Sprint Verification
# Executes all test cases across Days 1, 3, 4, and 5 to verify 100% functional correctness and zero regressions.

import unittest
from solo_recon_graphql.test_graphql_prototype import TestGraphQLPrototype
from test_day3_original_build import TestDay3OriginalBuild
from test_day4_pivot_build import TestDay4PivotBuild

def suite():
    s = unittest.TestSuite()
    s.addTest(unittest.makeSuite(TestGraphQLPrototype))
    s.addTest(unittest.makeSuite(TestDay3OriginalBuild))
    s.addTest(unittest.makeSuite(TestDay4PivotBuild))
    return s

if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite())
    if result.wasSuccessful():
        print("\n=======================================================")
        print("ALL SPRINT 2 TESTS PASSED! READY FOR FINAL SUBMISSION.")
        print("=======================================================")
    else:
        print("\n[ERROR] Test failures detected in master suite.")
