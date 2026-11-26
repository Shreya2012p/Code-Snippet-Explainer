from app.services.agent_service import verify_analysis

def test_agent_checks_improved_python_syntax():
    parsed={"parse_status":"success"}
    result=verify_analysis("x=1","python",{"summary":"Assign x.","explanation":"Stores 1.","steps":[],"improved_code":"x = 1"},parsed)
    assert result["passed"]
    assert any(c["name"]=="Improved-code syntax check" and c["passed"] for c in result["checks"])

def test_agent_flags_invalid_rewrite():
    parsed={"parse_status":"success"}
    result=verify_analysis("x=1","python",{"summary":"Assign x.","explanation":"Stores 1.","steps":[],"improved_code":"def broken(:"},parsed)
    assert not result["passed"]
