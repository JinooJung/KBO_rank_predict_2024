import pickle

################################ Real Results ################################
answers = [
    ["3월 종료 시점", "한기엔쓱엘두키삼롯케",[7/8, 5/6, 4/6, 5/8, 4/7, 4/8, 2/6, 2/7, 1/6, 1/8]]
]   


################################ Preprocessing ################################

prev_data_rate = [86/142, 79/141, 76/141, 75/142, 74/142, 73/142, 68/144, 61/143, 58/138, 58/141]
weight = pickle.load(open('weight.pkl', 'rb'))

team_names = ["LG", "KT", "SSG", "NC", "두산", "KIA", "롯데", "삼성", "한화", "키움"]
team_names_short = ["엘", "케", "쓱", "엔", "두", "기", "롯", "삼", "한", "키"]

player_answers = [
    ["진우", "한/롯케두기/키엘삼/쓱엔"],
    ["와지", "기한/케두삼/엔엘키/롯쓱"],
    ["다윤", "한기/삼두롯/엘케/키쓱엔"],
    ["희도", "두/한케기삼/롯엔엘키/쓱"],
    ["종윤", "한기/두케삼/엘키롯/쓱엔"],
    ["동건", "한/엘기롯삼/케엔두키/쓱"],
    ["재홍", "한/두삼키쓱/기엔롯케/엘"],
    ["지환", "한/롯삼엘기/키케쓱엔/두"],
    ["지훈", "엘/케쓱엔두기/롯/삼한키"],
    ["디지", "한기/엘두삼/롯케엔/키쓱"]
]
def player_answer_encoding(ans):
    ans = ans.split("/")
    for i in range(len(ans)):
        ans[i] = [team_names_short.index(x) for x in ans[i]]
    return ans

player_answers = [[ans[0], player_answer_encoding(ans[1])] for ans in player_answers]

################################ Helper Functions ################################

def answer_encoding(ans):
    return [team_names_short.index(x) for x in ans]


def score(ans):
    time = ans[0]
    ansen = answer_encoding(ans[1])
    gaps = [0 for _ in range(10)]
    for i in range(len(ansen)):
        gaps[i] = ans[2][ansen.index(i)] - prev_data_rate[i]
    best_index = gaps.index(max(gaps))
    worst_index = gaps.index(min(gaps))
    print("매우잘한팀:", team_names[best_index], ", 매우 못한팀:", team_names[worst_index])
    
    score_template = {"name":"", "score_by_team":[0 for _ in range(10)], "bonus":0, "final_score":0}
    scoreboard = []
    for pa in player_answers:
        temp = score_template.copy()
        temp["score_by_team"] = [0 for _ in range(10)]
        temp["name"] = pa[0]
        for i in range(len(ansen)):
            team_index = ansen[i]
            if(gaps[team_index]>=0):
                temp["score_by_team"][team_index] = float(weight[team_index][1]) * gaps[team_index] * 1000
            else:
                temp["score_by_team"][team_index] = float(weight[team_index][2]) * gaps[team_index] * 1000
                
            if(team_index in pa[1][0] or team_index in pa[1][1]):
                pass
            elif(team_index in pa[1][2] or team_index in pa[1][3]):
                temp["score_by_team"][team_index]*=-1
            else:
                temp["score_by_team"][team_index] = 0
                
                
        if(best_index in pa[1][0]):
            temp["bonus"]+=10/len(pa[1][0])
        if(worst_index in pa[1][3]):
            temp["bonus"]+=10/len(pa[1][3])
            
        if(sum(temp["score_by_team"])>=0):
            temp["final_score"] = sum(temp["score_by_team"]) * (1+temp["bonus"]/100)
        else:
            temp["final_score"] = sum(temp["score_by_team"]) * (1-temp["bonus"]/100)
          
        scoreboard.append(temp.copy())
        
    scoreboard = sorted(scoreboard, key=lambda x: x["final_score"], reverse=True)
    prev_score = -1
    for i in range(len(scoreboard)):
        if(scoreboard[i]["final_score"]!=prev_score):
            scoreboard[i]["rank"] = i+1
            prev_score = scoreboard[i]["final_score"]
        else:
            scoreboard[i]["rank"] = scoreboard[i-1]["rank"]
    
    return time, scoreboard


def latest_score():
    print(f"{answers[-1][0]}의 점수표!")
    _, scoreboard =  score(answers[-1])
    print("이름\t", end="")
    for team in team_names:
        print(team, end="\t")
    print("보너스\t최종점수\t순위")
    
    for s in scoreboard:
        print(s["name"], end="\t")
        for ss in s["score_by_team"]:
            print(f"{ss:.1f}", end="\t")
        print(f"{int(s['bonus'])}%\t{s['final_score']:.2f}\t\t{s['rank']}")
        
        


################################ Query ################################

def main():
    latest_score()
    
main()