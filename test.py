class Testing:
    val = 0
    @staticmethod
    def change_val():
        val = 20
    @staticmethod
    def print_val():
        print(Testing.val)


Testing.change_val()
Testing.print_val()