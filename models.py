from pydantic import BaseModel
from typing import List, Optional, Literal

class HistoryItem(BaseModel):
    date: str
    action: str
    user: str

class Task(BaseModel):
    id: str
    task_name: str
    explanation: str
    code_before: str
    code_after: Optional[str] = None
    test_output: str
    status: Literal['open', 'progress', 'fixed', 'failed']
    history: List[HistoryItem]
    github_link: Optional[str] = None
    codex_url: Optional[str] = None
    prompt: Optional[str] = None
    created_at: str

class SubTag(BaseModel):
    name: str
    type: Literal['bug', 'feature', 'scan', 'other']
    tasks: List[Task]

class Tag(BaseModel):
    name: str
    type: Literal['codex']
    sub_tags: List[SubTag]

class Template(BaseModel):
    id: str
    name: str
    description: str
    content: str
    tag: str

class TestRun(BaseModel):
    id: str
    module: str
    date: str
    totalTests: int
    passedTests: int
    failedTests: int
    duration: int  # in minutes
    coverage: float  # percentage
    testRunType: Literal['unit', 'integration', 'e2e']

class Bug(BaseModel):
    id: str
    module: str
    detectedDate: str
    severity: Literal['critical', 'high', 'medium', 'low']
    status: Literal['detected', 'fixing', 'fixed', 'verified']
    detectionMethod: Literal['ai', 'manual', 'automated']
    fixedDate: Optional[str] = None
    testPassAfterFix: Optional[bool] = None
    description: str

class ModuleCoverage(BaseModel):
    module: str
    date: str
    lineCoverage: float
    branchCoverage: float
    functionCoverage: float

class Analytics(BaseModel):
    totalTestRuns: int
    testPassRate: float
    bugsDetected: int
    bugsFixed: int
    fixSuccessRate: float
    averageCoverage: float

class TaskUpdate(BaseModel):
    task_name: Optional[str] = None
    explanation: Optional[str] = None
    code_before: Optional[str] = None
    code_after: Optional[str] = None
    test_output: Optional[str] = None
    status: Optional[Literal['open', 'progress', 'fixed', 'failed']] = None
    history: Optional[List[HistoryItem]] = None
    github_link: Optional[str] = None
    codex_url: Optional[str] = None
    prompt: Optional[str] = None

class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    tag: Optional[str] = None

