
import numpy as np

#create class 'solution' to make random_schedule then calculate the fitness 'H()' based on hard and soft constraint
class solution :
    def __init__(self,nurse,holidayes_requests):
        self.nurse_num=nurse
        self.schedule=[[],[],[],[],[],[],[]]
        self.holidayes_requests=holidayes_requests
        self.validation=True
        self.Reason = []
        self.conflict = 0
        self.fitness=0
        self.shifts=["M","A","N"]
        self.n_shifts_per_day = int((self.nurse_num*5)/7)#unKnown
    def random_schedule (self):
        for i in range(7):
            day=[]
            nurses_in_day=[]
            for j in range(self.n_shifts_per_day):
                nurse = np.random.randint(0,100000) % self.nurse_num +1
                while nurse in nurses_in_day  : #or  (nurse_load[nurse-1] == 3)  and (counter <= self.nurse_num):
                    nurse = np.random.randint(1,self.nurse_num + 1)
                nurses_in_day.append(nurse)
                element=self.shifts[j%3]+str(nurse)
                day.append(element)
            self.schedule[i]=day
    def working_days_for_nurses (self):
        working_days = []
            #getting all nurses working day in week
        for i in range(1 , self.nurse_num + 1) :
            nurse =str(i)
            IN = []
            nurse_shifts=[ self.shifts[0] + nurse ,self.shifts[1] + nurse ,self.shifts[2] + nurse]
            p=0
            for day in self.schedule:
                p+=1
                if (nurse_shifts[0]in  day) or(nurse_shifts[1] in day)or (nurse_shifts[2] in  day) :
                    IN.append(p)
            working_days.append(IN)
        return working_days
    def Hard_costrain(self): #first hard conrtaint check is all nurses working in range ( 3 : 5 ) day per week
        working_days = self.working_days_for_nurses()#getting working days for all nurses in week
            # working_days is the list has all nurses working days in week
        for i in range(len(working_days)) :
            if not len(working_days[i]) in range(4 ,7):
                self.validation = False
                self.Reason.append(str(len(working_days[i]))+"working day for nurse "+str(i+1)+")")
                self.conflict += 5
        # second hard constraint
        # this lines for split the gene into shifts instead days
        new_gene=[]
        for day in self.schedule : # abstract days from gene
            morning = []
            afternoon =[]
            night = []
            for j in day :# abstract shifts from days
                if self.shifts[0] in j:
                    morning.append(j)
                elif self.shifts[1] in j:
                    afternoon.append(j)
                elif self.shifts[2] in j :
                    night.append(j)
            new_gene.append(morning)
            new_gene.append(afternoon)
            new_gene.append(night)
           #discaver (night + morning)shifts conflict
        for i in range(len(new_gene)) : # i starting with 1 to 21 note(3 shift per day so 21 shifts per week)
            if (i+1)%3 == 0: # if (i+1)%3 == 0 this mean the shift is night
                for j in new_gene[i] : #take all night shifts sequential in one day
                    n = j.replace(self.shifts[2],"") # extract nurse in element || delete shift char 'N'
                    for k in new_gene[(i+1)%len(new_gene)]:
                       if n in k :
                           self.validation = False
                           self.Reason.append("night in day "+str(int(i/3+1))+" are conflict with the morning")
                           self.conflict +=5
    def calc_fitness(self):
        self.conflict = 0
        self.Reason = []
        self.validation = True

        self.Hard_costrain()

        wdays=self.working_days_for_nurses()
        for i in range(self.nurse_num):
            if self.holidayes_requests[i]%7 in wdays[i]:#[M1,A3,N5]
                self.Reason.append("Unsatisfied holiday for nurse "+str(i+1)+" at day "+str(self.holidayes_requests[i]%7))
                self.conflict +=1
        if self.conflict == 0 :
            self.fitness = 2
        else:
            self.fitness =round( 1/self.conflict, 4)

# create class 'Population' to make random different solutions and add new good solutions during Evolution
class Population :
    def __init__(self,n_population,n_nurses,holidayes_requests):
        self.parents = []
        self.sub_population =[]
        self.size=n_population
        self.n_nurses = n_nurses
        self.holidayes_requests=holidayes_requests

    def new_solution(self,solution,index):
        if index :
            for counter in range(len(self.parents) ):
                if solution.schedule == self.parents[counter].schedule :
                    return False
        else:
            for counter in range(len(self.sub_population) ):
                if solution.schedule == self.sub_population[counter].schedule :
                    return False
        return True

    def random_inti_(self):
        for counter in range(self.size):
            s= solution(self.n_nurses,self.holidayes_requests)
            s.random_schedule()
            while not self.new_solution(s,True): #chicking if the schedule is new solution | s:Solution ,True: for searching in first parents list
                s.random_schedule()
            s.calc_fitness()
            self.parents.append(s)
        print("population Created")

    def add(self,new_parents):
        for i in new_parents :
            if self.new_solution(i,False) :
                self.sub_population.append(i)

# create the solver class 'Differential_algorithm' to Select best solutions then Recombine and Mutate to find the best of the best solution
class Differential_algorithm :
    def __init__(self, population):
        self.population=population
        self.population.sub_population=list(self.population.parents)
        self.children = []
    #Select best solutions
    def Selection(self, evolute_growth):
        #sort depend on fitness
        self.population.sub_population.sort(key=lambda x: x.fitness, reverse=True)
        #select best of parant
        self.population.sub_population = self.population.sub_population[0:evolute_growth]
        # taking some of poor parent for taking any good genes from them
        poor_parent = []
        for i in range(3):# 3 will be great
            index = np.random.randint(int(self.population.size/3)) #poor parent will be in the third part in population
            poor_parent.append(self.population.parents[-index])
        self.population.add(poor_parent) #using add method for avoid duplication
        return self.population.sub_population[0]
    #Recombine the best solution to discover new parts on the search space
    def Recombination(self):#croosover
        self.children = []
        for par_1 in range(len(self.population.sub_population)):
            for par_2 in range(par_1+1,len(self.population.sub_population),) :
                child1 = solution(self.population.n_nurses,self.population.holidayes_requests )
                child2 = solution(self.population.n_nurses,self.population.holidayes_requests )
                child1.schedule=list(self.population.sub_population[par_1].schedule)
                child2.schedule=list(self.population.sub_population[par_2].schedule)
                temp = child1.schedule
                index=np.random.choice([2,3,4])
                child1.schedule[index:] = child2.schedule[index:]
                child2.schedule[index:]= temp[index:]
                child1.calc_fitness()
                child2.calc_fitness()
                self.children.append(child1)
                self.children.append(child2)
        self.children.sort(key = lambda x : x.fitness ,reverse=True )
        self.population.add(list(self.children[:10]))
    #Mutate the best solution to discover new parts on the search space
    def Mutation(self):
        #swap random day from first part of week with random day from second part of week
        for child in self.children :
            random_day1 = np.random.choice([0,1,2])
            random_day2 = np.random.choice([3,4,5,6])
            child.schedule.insert(random_day1,child.schedule.pop(random_day2))
            child.calc_fitness() #with any changing we must calc_fitness again

        self.children.sort(key = lambda x : x.fitness ,reverse=True )
        #print("child_mutation : ",self.children[0].fitness)
        self.population.add(list(self.children[:10]))

#this finction to print the final Scedule
def printing(x,nurse_size):
    # weak = [13*" "+"|sat",12*" "+"|sun",12*" "+"|mon",12*" "+"|tue",12*" "+"|wed",12*" "+"|thu",12*" "+"|fri"]
    weak = [13*" "+"|sat", "sun", "mon", "tue", "wed", "thu", "fri"]
    print(weak[0],end="")    
    for day in range(1,7):
        print(12*" "+"|"+weak[day],end="")
    print()
            
    for i in range(115):
        print("-",end="")
    print()
    
    for i in range(1,nurse_size+1):
        print("Nurse "+str(i)+" :",end="    ")
        for j in range(7):
            count = 0
            space=14
            print("|",end="")
            for k in x[j]:
                if int(k[1:]) == i:
                    print(k[0],end=" ")
                    count +=1
                    space-=1
            if count == 0:
                print("H",end="")
                count+=1
            for s in range(space):
                print(" ",end="")
        print("")


#taking the number of nurses
n_nurse=int(input("Enter Nurses Number:"))

#taking the holiday request from all nurses
holidayes_requests =[]
print("BY (sat = 1, sun = 2, ...,fri = 7)\nEnter holiday request for :")
for i in range(n_nurse) :
    holiday = int(input( "Nurse "+str(i+1)+" :"))
    while holiday not in range(1,8) :
        holiday = int (input("Enter valid day in range(1:7)day : "))
    holidayes_requests.append(holiday)
print("\t\t\t\t\t-------------------------------")

#taking the size of initialization population
size_population=int(input("Enter Population Size:"))

# take the best 30% solution for a signing them to Differential algorithm
Evolution_precentege = int(input("Evolution Grows:"))

# taking the loop size note(this number is "how much the solver will search for optimal solutions in loop")
loop_size = int(input("Evolution loop Size:"))

#create object from population class
population1 =Population(size_population,n_nurse,holidayes_requests)
print("Wait for creation....")

#initialize random population
population1.random_inti_()

print("\t\t\t\t\t-------------------------------")


#create solver object from Differential algorithm class
solver=Differential_algorithm(population1)

#select the top10 best sorted solutions
best_parent = solver.Selection(Evolution_precentege)

#solver while loop for trying to searching
while (not(best_parent.fitness > 1)) and (not(loop_size == 0 ) ):
    solver.Recombination()  #crosover all best_parents and get new children
    solver.Mutation() # mutate on all children
    best_parent = solver.Selection(Evolution_precentege)#take the best percentage % from all solution sorted to Evolute
    loop_size -= 1 # loop's increment


    #poor visialization for waiting
    if loop_size % 10 == 0 :
        print("#",end="")



#printing data the final best result
print("\n\t\t\t\t\t  Final Solution",
      "\nValidation_state :"+str(best_parent.validation),
      "\nFitness :"+str(best_parent.fitness),
      "\nConfilect number : "+str(best_parent.conflict))

if len(best_parent.Reason) !=0 :
    print("  Conflict Resons : ")
    for i in range(len(best_parent.Reason)):
        print("\t\t\t   ",i+1 , "- "+str(best_parent.Reason[i]))

#printing scedule
print("-------------------------\nFinal scedule :")
print();
printing(best_parent.schedule,n_nurse)
