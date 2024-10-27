def calculateBestBuildAgainst(heroes):
    itemsToUse = {}
    global matchOffenseP
    global matchOffenseM
    
    if len(heroes) != 5:
        print("5 HEROES INPUT NEEDED")
        return None
    
    for hero in heroes:
        hpairCurrent = weakness_table.get(hero)

        if hpairCurrent == None:
            print("Hero not found" + hero.name)
            return None
        
        heroStats = heroesStats.stats.get(hero)
        offenseImpact = heroStats[OFFENSE_STAT_POS] / getMatchOffenseScore(heroes)
        
        if hpairCurrent[1] == MAGIC:
            matchOffenseM += offenseImpact

        if hpairCurrent[1] == PHYSICAL:
            matchOffenseP += offenseImpact


        for pos, item in enumerate(hpairCurrent[0]):
            if ENABLE_ITEMS_PRIORITIES:
                posKoef = (0.05 * (len(hpairCurrent[0]) - 1 - pos))
            else:
                posKoef = 0

            if item in itemsToUse:
                itemsToUse[item] += offenseImpact + posKoef             # getting offense stats, since we need defend it
            else:
                itemsToUse[item] = offenseImpact + posKoef
    
    if DEBUG:
        print(sorted(itemsToUse.items(), key=lambda x: x[1], reverse=True))

    bootsItem = []
    
    for item in itemsToUse.items():
        if type(item[0]) == ItemBoots:
            bootsItem.append(item)
        
        # itemsToUse.pop(item)
    for boot in bootsItem:
        itemsToUse.pop(boot[0])
    
    if len(bootsItem) > 0:
        bootsItem = bootsItem[0]

    printMatchOffenseScores(matchOffenseM, matchOffenseP)
    # print(sorted(bootsItem, key=lambda x: x[1], reverse=True)[0][0])
    
    sortedItemsByScore = sorted(itemsToUse.items(), key=lambda x: x[1], reverse=True)

    # if DO_FIXING:
    #     doPrefixing(sortedItemsByScore)


    print(f"{WHITE}[{BLUE} Hero Results {WHITE}]\n")

    if DO_OPTIMIZATION_BUILD:
        optimizedItems = doCombinationCrackingFrom(matchHeroes, sortedItemsByScore, bootsItem)
        if optimizedItems != None:
            optimizedItems = sorted(optimizedItems, key=lambda x: x[1], reverse=True)
        else:
            optimizedItems = sortedItemsByScore
        stats = calculateStats(matchHeroes, optimizedItems, bootsItem)
    else:
        optimizedItems = sortedItemsByScore
        stats = calculateStats(matchHeroes, sortedItemsByScore, bootsItem)

    printHeroResults(stats)

    printTitle("Recommended Items", '\n')
    
    if len(bootsItem) != 0:
        printTitle("Boots")
        t = f"{YELLOW}M" if types[bootsItem[0]] else f"{RED}P"
        print(f"{WHITE}[{t}{WHITE}][{GREEN}{bootsItem[0].name:<20}{WHITE}][ {CYAN}{round(bootsItem[1], 3)}{WHITE} ]")

    printTitle("Armor", '\n')

    for item in optimizedItems[:MATCH_ITEMS_COUNT]:
        t = f"{YELLOW}M" if types[item[0]] else f"{RED}P"
        print(f"{WHITE}[{t}{WHITE}][{GREEN}{item[0].name:<20}{WHITE}][ {CYAN}{round(item[1], 3):<5}{WHITE} ]")

    if DO_OPTIMIZATION_BUILD:
        printOverallStatistics("Overall Reduction (O):", stats)
    
    stats = calculateStats(matchHeroes, sortedItemsByScore, bootsItem)
    print(f'\n{WHITE}[ {BLUE}Overall Reduction (N): {WHITE}][{CYAN}{round(stats[1] * 100):>3}%{WHITE} ]', end='')

    if matchOffenseM != 0:
        print(f"[ {YELLOW}{round(stats[2] / matchOffenseM * 100):>3}%{WHITE} ]",end='')
    if matchOffenseP != 0:
        print(f'[ {RED}{round(stats[3] / matchOffenseP * 100):>3}%{WHITE} ]\n',end='')
    print()

calculateBestBuildAgainst(matchHeroes)

