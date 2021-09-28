lists_points = [[1,2,3,4,5],[3,2,1,4,5],[2,4,5,1,3]]
lists_dists = [[0.1,0.2,0.3,0.4,0.5],[0.2,0.4,0.3,0.7,0.2],[0.4,0.1,0.2,0.5,0.3]]
hubs_cnt = len(lists_points)
points_cnt = len(lists_points[0])
lists_length = 0
hubfeats = {}
featslst = []
for listElem in lists_points:
    lists_length += len(listElem)
currenthub = 0
pph = int(points_cnt / hubs_cnt)
for i in range(points_cnt):
    #mindist_lst_idx+1 = minhub
    mindist_lst = min(lists_dists, key=min) # [0.1, 0.2, 0.3]
    mindist_lst_idx = lists_dists.index(mindist_lst) # 0
    minpoint_lst = lists_points[mindist_lst_idx] # [1, 2, 3]
    minpoint_lst_idx = lists_points.index(minpoint_lst) # 0
    mindist = min(mindist_lst) # 0.1
    mindist_idx = lists_dists[mindist_lst_idx].index(mindist)
    minpoint = minpoint_lst[mindist_idx] # 1
    minpoint_idx = lists_points[minpoint_lst_idx].index(minpoint)
    print(lists_points)
    print(lists_dists)
    print(mindist)
    print(minpoint)
    featslst.append(minpoint)
    hubfeats[currenthub] = featslst
    del lists_points[minpoint_lst_idx][minpoint_idx]
    del lists_dists[mindist_lst_idx][mindist_idx]
    for p, d in zip(lists_points, lists_dists):
        try:
            idx = p.index(minpoint)
            p.remove(minpoint)
            del d[idx]
        except:
            pass
    if len(mindist_lst) == 0:
        del lists_points[minpoint_lst_idx]
        del lists_dists[mindist_lst_idx]
    try:
        if len(hubfeats) == pph:
            del lists_points[minpoints_lst_idx]
            del lists_dists[mindist_lst_idx]
    except:
        pass
    currenthub += 1
print(hubfeats)
    