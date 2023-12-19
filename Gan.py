import sys
class TradeExecution:
    def __init__(self):    
        self.paired_trades = []         #for trades which are paired and completed
        self.inventory = {}             #for inventory to save the current inventory
        self.pnl_total=0                #final pnl
    def read_trades(self, trades_file): #to read trades and then pair them
        with open(trades_file, 'r') as file:
            header = file.readline().strip().split(',')
            for line in file:   #reading data from file line by line
                trade = line.strip().split(',') #splitting the line by ,
                time = int(trade[0])            #getting time of that trade
                symbol = trade[1]               #getting symbol of that trade
                side = trade[2]                 #getting side of that trade
                price = float(trade[3])         #getting price of that trade
                quantity = int(trade[4])        #getting quantity of that trade
                if symbol not in self.inventory:    #adding inventory to new symbol
                    self.inventory[symbol] = {'B': [], 'S': []}
                if side == 'B': #if comming trade_side is B then trying to pair it with side S and if no pair found then adding it to inventory
                    self.execute_trades(symbol,self.inventory[symbol],quantity,price,time,'B','S')
                elif side == 'S': #if comming trade_side is S then trying to pair it with side B and if no pair found then adding it to inventory
                    self.execute_trades(symbol,self.inventory[symbol],quantity,price,time,'S','B')    
    def pnlcal(self,open_side,open_price,close_price):
        if open_side=='B':
            return round((close_price-open_price), 2)
        else:
            return round((open_price-close_price), 2)
    def execute_trades(self,symbol,trade,quantity,price,time,close_side,open_side):
        quantity_closed = quantity #defining close side parameters
        close_price = price
        close_time = time
        while quantity_closed > 0 and trade[open_side]: #trying to pair close side with available open side
            open_trade = trade[open_side].pop(0)    #in fifo manner taking open side traade
            open_quantity = open_trade[1]   #defining opening side parameters
            open_price = open_trade[2]
            open_time = open_trade[0]
            temp = quantity_closed          #
            paired_quantity = min(quantity_closed, open_quantity)
            pnl = paired_quantity * self.pnlcal(open_side,open_price,close_price)
            self.paired_trades.append({
                'OPEN TIME': open_time,
                'CLOSE TIME': close_time,
                'SYMBOL': symbol,
                'QUANTITY': paired_quantity,
                'PNL': pnl,
                'OPEN SIDE': open_side,
                'CLOSE SIDE': close_side,
                'OPEN PRICE': open_price,
                'CLOSE PRICE': close_price
            })
            self.pnl_total += pnl
            quantity_closed -= paired_quantity
            if quantity_closed == 0 and open_quantity - temp != 0: #if quantity of open side is > quantity of close side the inserting at front the remaining open side trade inventory
                trade[open_side].insert(0,(open_time, open_quantity - temp, open_price))
        if quantity_closed!=0:  #if quantity of close side is >quantity of open side then appending the remaining close side in the inventory of that trade
            trade[close_side].append((time, quantity_closed, close_price))
    def print_trade_pairs(self,output): #writning the trade pairs to output.csv file
        with open(output, 'w') as csvfile:
            csvfile.write(','.join(['OPEN_TIME', 'CLOSE_TIME', 'SYMBOL', 'QUANTITY', 'PNL', 'OPEN_SIDE', 'CLOSE_SIDE', 'OPEN_PRICE', 'CLOSE_PRICE']))
            csvfile.write('\n')
            for trade in self.paired_trades:
                csvfile.write(','.join(str(trade[key]) for key in trade))
                csvfile.write('\n')
            csvfile.write(f'{self.pnl_total:.2f}')
            csvfile.write('\n')
processor = TradeExecution()    #making object of the class
processor.read_trades(sys.argv[1])  #reading and execuring the trades
processor.print_trade_pairs("output.csv")   #saving the output to output.csv file