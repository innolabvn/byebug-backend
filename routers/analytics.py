from fastapi import APIRouter
from typing import List

from models import TestRun, Bug, ModuleCoverage, Analytics
from database import get_database

router = APIRouter()

@router.get("/analytics/test-runs", response_model=List[TestRun])
async def get_test_runs():
    """Return stored test run records."""
    # Query test run records
    db = get_database()
    runs = await db.byebug.test_runs.find().to_list(None)
    return runs

@router.get("/analytics/bugs", response_model=List[Bug])
async def get_bugs():
    """Return detected bugs."""
    db = get_database()
    bugs = await db.byebug.bugs.find().to_list(None)
    # Fetch bug list
    return bugs

@router.get("/analytics/coverage", response_model=List[ModuleCoverage])
async def get_coverage():
    """Return module coverage data."""
    db = get_database()
    # Retrieve coverage stats
    cov = await db.byebug.coverage.find().to_list(None)
    return cov

@router.get("/analytics/summary", response_model=Analytics)
async def get_summary():
    """Return aggregated analytics summary."""
    db = get_database()
    # Aggregate statistics from collections
    runs = await db.byebug.test_runs.find().to_list(None)
    bugs_list = await db.byebug.bugs.find().to_list(None)
    coverage_list = await db.byebug.coverage.find().to_list(None)

    total_test_runs = len(runs)
    total_tests = sum(t["totalTests"] for t in runs)
    passed_tests = sum(t["passedTests"] for t in runs)
    test_pass_rate = (passed_tests / total_tests * 100) if total_tests else 0

    bugs_detected = len(bugs_list)
    bugs_fixed = len([b for b in bugs_list if b["status"] in ("fixed", "verified")])
    fix_success_rate = (bugs_fixed / bugs_detected * 100) if bugs_detected else 0

    average_coverage = (
        sum(c["lineCoverage"] for c in coverage_list) / len(coverage_list)
        if coverage_list else 0
    )

    return Analytics(
        totalTestRuns=total_test_runs,
        testPassRate=test_pass_rate,
        bugsDetected=bugs_detected,
        bugsFixed=bugs_fixed,
        fixSuccessRate=fix_success_rate,
        averageCoverage=average_coverage,
    )

