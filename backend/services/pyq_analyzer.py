"""Stateless analysis of user-supplied previous-year question text."""
import re
from collections import Counter
STOPWORDS=set("what which with from that this the and for are explain describe write short note notes define between give example state using about discuss how why does into their types question answer marks mark following briefly derive prove find calculate given show list each any all your you its can not use based an in on of to is a or by as at be it".split())
def analyze_pyqs(papers):
    if not 1 <= len(papers) <= 20:
        raise ValueError("Provide 1 to 20 papers")
    questions=[]
    for paper in papers:
        year,content=paper.get("year"),paper.get("text")
        if not isinstance(year,int) or not 2000<=year<=2100 or not isinstance(content,str) or len(content)>30000:
            raise ValueError("Invalid year or paper text")
        for line in content.splitlines():
            line=re.sub(r"^\s*(?:Q\s*\d+\s*[.):]?|\d+\s*[.):])\s*","",line.strip(),flags=re.I)
            if len(line)<8: continue
            match=re.search(r"[\[(]\s*(\d{1,2})\s*(?:marks?)?\s*[\])]\s*$",line,re.I)
            marks=int(match.group(1)) if match else None
            if match: line=line[:match.start()].strip()
            questions.append({"year":year,"question":line,"marks":marks})
    if not questions or len(questions)>500: raise ValueError("Provide 1 to 500 question lines")
    counts=Counter()
    years={}
    for q in questions:
        for term in set(re.findall(r"[a-z][a-z0-9-]{2,}",q["question"].lower()))-STOPWORDS:
            counts[term]+=1
            years.setdefault(term,set()).add(q["year"])
    return {"paper_count":len(papers),"question_count":len(questions),"questions":questions,
      "recurring_keywords":[{"keyword":term,"question_count":count,"years":sorted(years[term])} for term,count in sorted(counts.items(),key=lambda x:(-x[1],x[0]))[:20]],
      "methodology":"Keyword occurrence per supplied question line; not a prediction of future exam questions.",
      "limitations":["Synonyms counted separately","One line treated as one question","Marks only when supplied"]}
