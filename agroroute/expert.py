"""Transparent educational rule engine, not pesticide advice."""
from dataclasses import dataclass
@dataclass
class Conclusion:
    facts: dict
    trace: list[str]

def forward_chain(disease: str, severity: str, rain: bool=False, accessible: bool=True) -> Conclusion:
    facts={'disease':disease,'severity':severity,'rain':rain,'accessible':accessible}
    trace=[]
    if disease!='Unknown' and disease!='Healthy':
        facts['needs_inspection']=True; trace.append('R1: suspected disease -> needs inspection')
    if severity=='High' and facts.get('needs_inspection'):
        facts['priority']='Urgent'; trace.append('R2: high severity + disease -> urgent inspection')
    elif facts.get('needs_inspection'):
        facts['priority']='Routine'; trace.append('R3: disease -> routine inspection')
    else:
        facts['priority']='Monitor'; trace.append('R4: no suspected disease -> monitor')
    if rain:
        facts['spraying_allowed']=False; trace.append('R5: rain -> spraying prohibited in this demo')
    else:
        facts['spraying_allowed']='Requires verified label and conditions'; trace.append('R6: verify pesticide label and conditions before any action')
    if not accessible:
        facts['dispatch_allowed']=False; trace.append('R7: inaccessible zone -> no rover dispatch')
    else:
        facts['dispatch_allowed']=True; trace.append('R8: accessible zone -> dispatch feasible')
    return Conclusion(facts,trace)

def backward_chain(conclusion: Conclusion, goal: str):
    if goal not in conclusion.facts: return False, ['Goal not derivable from current facts']
    return bool(conclusion.facts[goal]), [f'Goal {goal}: {conclusion.facts[goal]}']+conclusion.trace
