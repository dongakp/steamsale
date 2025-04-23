최대한 백엔드 팀의 프로젝트를 적용했으나 사실상 챗GPT를 혹사시킨 결과물이기 때문에 너무 많은 변동사항이 있어 아직 Main에 merge안 하시는걸 추천드립니다


상희님이 구현하신 게임 수에 숫자 이외의 텍스트가 들어가면 error 처리하는 것과 game_list 정렬 토글바도 추가했습니다.

더욱 확실하게 이를 보여주기 위해 
<input type="number" name="count" class="form-control form-control-sm mb-2"
                            placeholder="최대 게임 수를 입력하세요" min="1" value="{{ request.POST.count|default:'' }}">
에서 
<input type="text" name="count" class="form-control form-control-sm mb-2"
                            placeholder="최대 게임 수를 입력하세요" value="{{ request.POST.count|default:'' }}">

input type을 text로 교체했습니다. 또한 공백 이외에도 0이 들어가는 경우 역시 error 처리했습니다.
