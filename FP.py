class Node:
    def __init__(self, word, word_count=0, parent=None, link=None):
        # Initialize node attributes
        self.word = word              # Item label
        self.word_count = word_count  # Frequency count of the item
        self.parent = parent          # Reference to parent node
        self.link = link              # Link to the next node with the same label
        self.children = {}            # Dictionary to store child nodes

# Define the FPTree class to construct and manage the FP Growth tree
class FPTree:
    def __init__(self, data, minsup=2):
        self.data = data               # Transaction data
        self.minsup = minsup           # Minimum support value
        self.root = Node(word="Null", word_count=1)  # Create the root node with label "Null" and count 1
        self.wordlinesort = []          # List to store sorted item information for transactions
        self.nodetable = []             # List to store item information
        self.wordsortdic = []           # List to store sorted item information
        self.worddic = {}               # Dictionary to store item frequency counts
        self.wordorderdic = {}          # Dictionary to store item ordering
        self.construct(data)            # Call the construct method to build the FP Growth tree

    # Construct the FP Growth tree
    def construct(self, data):
        # Calculate the frequency of each item in transactions
        for tran in data:
            for word in tran:
                if word in self.worddic:
                    self.worddic[word] += 1
                else:
                    self.worddic[word] = 1
        wordlist = list(self.worddic.keys())
        # Filter out items with frequency below the minimum support value
        for word in wordlist:
            if self.worddic[word] < self.minsup:
                del self.worddic[word]
        # Sort items based on their frequency and create a dictionary for ordering
        self.wordsortdic = sorted(self.worddic.items(), key=lambda x: (-x[1], x[0]))
        t = 0
        for i in self.wordsortdic:
            word = i[0]
            wordc = i[1]
            self.wordorderdic[word] = t
            t += 1
            wordinfo = {'wordn': word, 'wordcc': wordc, 'linknode': None}
            self.nodetable.append(wordinfo)
        # Build the FP Growth tree
        for line in data:
            supword = [word for word in line if word in self.worddic]
            if len(supword) > 0:
                sortsupword = sorted(supword, key=lambda k: self.wordorderdic[k])
                self.wordlinesort.append(sortsupword)
                R = self.root
                for word in sortsupword:
                    if word in R.children:
                        R.children[word].word_count += 1
                        R = R.children[word]
                    else:
                        R.children[word] = Node(word=word, word_count=1, parent=R, link=None)
                        R = R.children[word]
                        for wordinfo in self.nodetable:
                            if wordinfo["wordn"] == R.word:
                                if wordinfo["linknode"] is None:
                                    wordinfo["linknode"] = R
                                else:
                                    iter_node = wordinfo["linknode"]
                                    while iter_node.link is not None:
                                        iter_node = iter_node.link
                                    iter_node.link = R
    
    # Construct conditional transaction based on a node
    def condtreetran(self, N):
        if N.parent is None:
            return None
        
        condtreeline = []
        while N is not None:
            line = []
            PN = N.parent
            while PN.parent is not None:
                line.append(PN.word)
                PN = PN.parent
            line = line[::-1]
            for _ in range(N.word_count):
                condtreeline.append(line)
            N = N.link
        return condtreeline
    
    # Find frequent itemsets using the FP Growth algorithm
    def find_frequent_itemsets(self, parentnode=None):
        if len(self.root.children) == 0:
            return None
        result = []
        sup = self.minsup
        revtable = self.nodetable[::-1]
        # Traverse the nodetable in reverse order to find frequent itemsets
        for n in revtable:
            # Create a frequent itemset (fqset) by adding the current node's item to the parentnode
            fqset = (n['wordn'],) if parentnode is None else (n['wordn'],) + parentnode[0]
            fqset_count = n['wordcc']
            result.append([fqset, fqset_count])
            
            # Construct the conditional transaction based on the current node's link
            condtran = self.condtreetran(n['linknode'])
            
            # If there is a conditional transaction, create a new FPTree instance for it
            if condtran is not None:
                contree = FPTree(condtran, sup)
                
                # Recursively find frequent itemsets for the conditional tree
                conwords = contree.find_frequent_itemsets([fqset, fqset_count])
                
                # If there are frequent itemsets in the conditional tree, append them to the result list
                if conwords is not None:
                    result.extend(conwords)
        return result

    def print_frequent_itemsets(self, frequent_itemsets):
        # Initialize variables for tracking single itemset and output line
        current_single_item = None
        output_line = []
        i=1
        for itemset, support in frequent_itemsets:
            if len(itemset) == 1:
                # If a new single itemset is encountered, print the current line and reset
                if current_single_item:
                    if len(output_line) > 1:  # Check if there's more than one element in the line
                        print(f"ROW {i}: ",end='')
                        print('    '.join(output_line))  # Print the line with 5 spaces gap
                        i=i+1
                current_single_item = itemset
                output_line = [f"[{' '.join(itemset)}] {support}"]
            else:
                # Append to the current line if not a new single itemset
                output_line.append(f"[{' '.join(itemset)}] {support}")
        # Print the last line
        if current_single_item and len(output_line) > 1:
            print('    '.join(output_line))

# Define the main function
min_sup = 3
test_data =  [
    ['M', 'O', 'N', 'K', 'E', 'Y'],
    ['D', 'O', 'N', 'K', 'E', 'Y'],
    ['M', 'A', 'K', 'E'],
    ['M', 'U', 'C', 'K', 'Y'],
    ['C', 'O', 'O', 'K', 'I', 'E']
]

# Create an instance of FPTree 
deduplicated_data = [list(set(transaction)) for transaction in test_data]
fp_tree = FPTree(deduplicated_data , min_sup)

#find frequent itemsets
frequent_itemsets = fp_tree.find_frequent_itemsets()

# Print the frequent itemsets
fp_tree.print_frequent_itemsets(frequent_itemsets)
