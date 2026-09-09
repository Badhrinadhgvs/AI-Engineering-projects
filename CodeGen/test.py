from app.LLM import CodeGen

a = """
class Node:
    def __init__(self, data):
        self.data = data  # Stores the actual data
        self.next = None  # Points to the next node (initially None)


class LinkedList:
    def __init__(self):
        self.head = None  # The list starts empty, so head is None

    def insert_at_end(self, data):
        new_node = Node(data)
        
        # If the list is empty, make the new node the head
        if self.head is None:
            self.head = new_node
            return
        
        # Otherwise, traverse to the last node
        current = self.head
        while current.next is not None:
            current = current.next
        
        # Link the last node's next pointer to the new node
        current.next = new_node

    def display(self):
        if self.head is None:
            print("The list is empty.")
            return
            
        current = self.head
        while current is not None:
            print(current.data, end=" -> ")
            current = current.next
        print("None")  # Marks the end of the list


# --- Example Usage ---
if __name__ == "__main__":
    # 1. Create a new linked list
    my_list = LinkedList()

    # 2. Insert elements into the list
    my_list.insert_at_end(10)
    my_list.insert_at_end(20)
    my_list.insert_at_end(30)

    # 3. Print the linked list
    print("Singly Linked List elements:")
    my_list.display()

"""


c = CodeGen(a, "JAVA")
print(c.main())
