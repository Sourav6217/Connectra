"""Skill test MCQ bank — 5 questions per skill, 90 second timer."""

SKILL_TESTS = {
    "Python": [
        {"q": "What does `list(range(3))` return?", "opts": ["[1,2,3]","[0,1,2]","[0,1,2,3]","Error"], "ans": 1},
        {"q": "Which is used for a key-value store in Python?", "opts": ["list","tuple","dict","set"], "ans": 2},
        {"q": "What does `len('hello')` return?", "opts": ["4","5","6","Error"], "ans": 1},
        {"q": "What keyword defines a function?", "opts": ["func","def","function","lambda"], "ans": 1},
        {"q": "What is the output of `2 ** 3`?", "opts": ["6","8","5","9"], "ans": 1},
    ],
    "SQL": [
        {"q": "Which clause filters rows AFTER grouping?", "opts": ["WHERE","HAVING","FILTER","LIMIT"], "ans": 1},
        {"q": "What does `SELECT DISTINCT` do?", "opts": ["Counts rows","Removes duplicates","Sorts results","Joins tables"], "ans": 1},
        {"q": "Which JOIN returns all rows from both tables?", "opts": ["INNER","LEFT","RIGHT","FULL OUTER"], "ans": 3},
        {"q": "Which aggregate counts non-null values?", "opts": ["SUM","MAX","COUNT","AVG"], "ans": 2},
        {"q": "What does `GROUP BY` do?", "opts": ["Sorts data","Groups rows by column values","Filters rows","Joins tables"], "ans": 1},
    ],
    "Machine Learning": [
        {"q": "What does overfitting mean?", "opts": ["Model performs well on train only","Model underfits data","Model has high bias","Model has low variance"], "ans": 0},
        {"q": "Which algorithm is for classification?", "opts": ["Linear Regression","K-Means","Logistic Regression","PCA"], "ans": 2},
        {"q": "What is the purpose of cross-validation?", "opts": ["Speed up training","Estimate generalization","Reduce features","Normalize data"], "ans": 1},
        {"q": "Which metric is used for imbalanced classification?", "opts": ["Accuracy","F1 Score","MSE","R²"], "ans": 1},
        {"q": "What does `train_test_split` do?", "opts": ["Normalizes data","Splits dataset","Trains model","Evaluates model"], "ans": 1},
    ],
    "React": [
        {"q": "What hook manages local state?", "opts": ["useEffect","useState","useRef","useCallback"], "ans": 1},
        {"q": "What does JSX stand for?", "opts": ["JavaScript XML","Java Syntax Extension","JSON eXtended","JavaScript Extension"], "ans": 0},
        {"q": "How do you pass data to a child component?", "opts": ["State","Context","Props","Refs"], "ans": 2},
        {"q": "Which hook handles side effects?", "opts": ["useState","useEffect","useMemo","useRef"], "ans": 1},
        {"q": "What is the virtual DOM?", "opts": ["A browser API","A lightweight JS representation of DOM","A CSS framework","A state manager"], "ans": 1},
    ],
    "AWS": [
        {"q": "What does S3 stand for?", "opts": ["Simple Storage Service","Secure Server System","Scalable Storage System","Simple Server Service"], "ans": 0},
        {"q": "Which service runs serverless functions?", "opts": ["EC2","Lambda","RDS","S3"], "ans": 1},
        {"q": "What is an IAM Role?", "opts": ["A database","Permissions assigned to AWS resources","A virtual machine","A storage bucket"], "ans": 1},
        {"q": "What is VPC?", "opts": ["A virtual CPU","Virtual Private Cloud","A caching layer","A DNS service"], "ans": 1},
        {"q": "Which service is for relational databases?", "opts": ["DynamoDB","Redshift","RDS","S3"], "ans": 2},
    ],
    "Docker": [
        {"q": "What is a Dockerfile?", "opts": ["A running container","A script to build an image","A container network","A volume"], "ans": 1},
        {"q": "Which command runs a container?", "opts": ["docker build","docker run","docker pull","docker push"], "ans": 1},
        {"q": "What is a Docker image?", "opts": ["A running instance","A read-only template","A network","A volume"], "ans": 1},
        {"q": "What does `docker-compose` do?", "opts": ["Builds images","Manages multi-container apps","Pushes to registry","Scans for vulnerabilities"], "ans": 1},
        {"q": "What is the default Docker network driver?", "opts": ["host","none","bridge","overlay"], "ans": 2},
    ],
    "Risk Analytics": [
        {"q": "What does VaR measure?", "opts": ["Expected profit","Maximum potential loss at a confidence level","Average return","Portfolio size"], "ans": 1},
        {"q": "What is a credit score used for?", "opts": ["Measuring stock performance","Assessing loan default probability","Calculating market risk","Pricing options"], "ans": 1},
        {"q": "What is Monte Carlo simulation used for?", "opts": ["Exact calculation","Approximating outcomes through random sampling","Training ML models","Hedging risk"], "ans": 1},
        {"q": "What does Basel III regulate?", "opts": ["Tax reporting","Bank capital requirements","Stock market rules","Insurance policies"], "ans": 1},
        {"q": "What is counterparty risk?", "opts": ["Risk of market crash","Risk that one party defaults","Operational risk","Liquidity risk"], "ans": 1},
    ],
    "Pandas": [
        {"q": "Which method reads a CSV file?", "opts": ["pd.read_csv()","pd.open_csv()","pd.load_csv()","pd.import_csv()"], "ans": 0},
        {"q": "What does `df.shape` return?", "opts": ["Column names","Data types","(rows, columns)","Index"], "ans": 2},
        {"q": "How do you select column 'age' from df?", "opts": ["df.age","df['age']","df.get('age')","All of these"], "ans": 3},
        {"q": "What does `df.dropna()` do?", "opts": ["Fills NaN","Removes rows with NaN","Renames columns","Sorts data"], "ans": 1},
        {"q": "Which method groups data?", "opts": ["df.sort_values","df.groupby","df.pivot","df.merge"], "ans": 1},
    ],
    "Streamlit": [
        {"q": "How do you display a title?", "opts": ["st.header()","st.title()","st.text()","st.write()"], "ans": 1},
        {"q": "What does `st.session_state` store?", "opts": ["CSS styles","Variables across reruns","Page HTML","Database connections"], "ans": 1},
        {"q": "Which function creates a sidebar?", "opts": ["st.panel()","st.aside()","st.sidebar","st.drawer()"], "ans": 2},
        {"q": "What does `st.rerun()` do?", "opts": ["Stops app","Reruns the script","Clears cache","Resets state"], "ans": 1},
        {"q": "How do you display a chart?", "opts": ["st.show_chart()","st.plot()","st.plotly_chart()","st.render()"], "ans": 2},
    ],
    "JavaScript": [
        {"q": "What does `typeof null` return?", "opts": ["null","undefined","object","string"], "ans": 2},
        {"q": "Which method adds to end of array?", "opts": ["shift","push","pop","unshift"], "ans": 1},
        {"q": "What does `===` check?", "opts": ["Value only","Type only","Value and type","Reference equality"], "ans": 2},
        {"q": "What is a Promise?", "opts": ["A variable","Object representing async operation","A function","A class"], "ans": 1},
        {"q": "What does `Array.map()` return?", "opts": ["Original array","New transformed array","Undefined","Boolean"], "ans": 1},
    ],
}

DEFAULT_QUESTIONS = [
    {"q": "This skill requires hands-on experience. How many years do you have?", "opts": ["0-1","1-3","3-5","5+"], "ans": 2},
    {"q": "Which best describes your proficiency?", "opts": ["Beginner","Intermediate","Advanced","Expert"], "ans": 2},
    {"q": "Have you used this in a production project?", "opts": ["Never","Once","Multiple times","Extensively"], "ans": 2},
    {"q": "Can you mentor others in this skill?", "opts": ["No","With guidance","Yes","I wrote documentation for it"], "ans": 2},
    {"q": "How recently have you used this skill?", "opts": ["Never","1+ year ago","Last 6 months","Currently"], "ans": 3},
]

def get_questions(skill: str) -> list:
    return SKILL_TESTS.get(skill, DEFAULT_QUESTIONS)
