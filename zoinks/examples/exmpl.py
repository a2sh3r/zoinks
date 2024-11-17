from zoinks.macros import requires_lock, guards_variable


@requires_lock('my_lock')
@guards_variable('shared_var')
def example_function():
    # 'shared_var' protection is required
    shared_var = 10
    print(shared_var)

