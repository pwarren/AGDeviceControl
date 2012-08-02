#!/usr/bin/env python

'''This module implements a Finite State Machine (FSM).

Taken from the Active State Programmers Network Cookbook
http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/146262
License is listed as "freely available for review and use",
ie., public domain. [ed.]  Minor tweaks for use with AGDeviceControl
by D. Edmundson.

In addition to state this FSM also maintains a user defined "something".
This "something" is effectively memory, so this FSM could be considered
a Push-down Automata (PDA) since a PDA is a FSM + memory.

The following describes how the FSM works, but you will probably also need
to see the example function to understand how the FSM is used in practice.

You define an FSM by building tables of transitions.
For a given input symbol the process() method uses these tables 
to decide what action to call and what the next state will be. 
The FSM has a table of transitions that associate:
        (input_symbol, current_state) --> (action, next_state)
where "action" is a function you define. The symbols and states 
can be any objects. You use the add_transition() and add_transition_list() 
methods to add to the transition table. The FSM also has a table
of transitions that associate:
        (current_state) --> (action, next_state)
You use the add_transition_any() method to add to this transition table.
The FSM also has one default transition that is not associated
with any specific input_symbol or state. You use the 
set_default_transition() method to set the default transition.

When an action function is called it is passed a reference to the FSM.
The action function may then access attributes of the FSM such as
input_symbol, current_state, or "something". The "something" attribute 
can be any object that you want to pass along to the action functions.
It is not used by the FSM. For parsing you would typically pass a list 
to be used as a stack.

The processing sequence is as follows.
The process() method is given an input_symbol to process.
The FSM will search the table of transitions that associate:
        (input_symbol, current_state) --> (action, next_state) 
If the pair (input_symbol, current_state) is found then 
process() will call the associated action function and then set the 
current state to the next_state.

If the FSM cannot find a match for (input_symbol, current_state)
it will then search the table of transitions that associate:
        (current_state) --> (action, next_state)
If the current_state is found then the process() method will call 
the associated action function and then set the current state to 
the next_state. Notice that this table lacks an input_symbol. 
It lets you define transitions for a current_state and ANY input_symbol.
Hence, it is called the "any" table. Remember, it is always checked
after first searching the table for a specific (input_symbol, current_state).

For the case where the FSM did not match either of the previous two cases
the FSM will try to use the default transition. If the default transition
is defined then the process() method will call the associated action function
and then set the current state to the next_state. This lets you define 
a default transition as a catch-all case. You can think of it as an 
exception handler. There can be only one default transition.

Finally, if none of the previous cases are defined for an input_symbol 
and current_state then the FSM will raise an exception. 
This may be desirable, but you can always prevent this just by 
defining a default transition.

Noah Spurrier 20020822
'''

class ExceptionFSM(Exception):
    '''This is the FSM Exception class.'''
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return `self.value`


class FSM:
    '''This is a Finite State Machine (FSM).
    '''

    def __init__(self, initial_state, callable):
        '''This creates the FSM. 
        You set the initial state here. The "callable" object is called
        with argument action
        '''
        # Map (input_symbol, current_state) --> (action, next_state).
        self.state_transitions = {}
        # Map (current_state) --> (action, next_state).
        self.state_transitions_any = {}
        self.default_transition = None
        
        self.input_symbol = None
        self.initial_state = initial_state
        self.current_state = self.initial_state
        self.callable = callable


    def reset (self):
        '''This sets the current_state to the initial_state and
        sets input_symbol to None.
        The initial state was set by the constructor __init__().
        '''
        self.current_state = self.initial_state
        self.input_symbol = None


    def add_transition (self, input_symbol, state, action, next_state):
        '''This adds a transition that associates
                (input_symbol, current_state) --> (action, next_state)
        The action may be set to None in which case the process() method 
        will ignore the action and only set the next_state.
           
        You can also set transitions for a list of symbols by using
        add_transition_list().
        '''
        self.state_transitions[(input_symbol, state)] = (action, next_state)


    def add_transition_list (self, list_input_symbols, state, action, next_state):
        '''This adds the same transition for lots of different input symbols.
        You can pass a list or a string. Note that it is handy to use
        string.digits, string.whitespace, string.letters, etc. to add
        transitions that match character classes.
        '''
        for input_symbol in list_input_symbols:
            self.add_transition (input_symbol, state, action, next_state)


    def add_transition_any (self, state, action, next_state):
        '''This adds a transition that associates
                (current_state) --> (action, next_state)
        The process() method checks these associations if it cannot
        first find a match of an (input_symbol, current_state).
        '''
        self.state_transitions_any [state] = (action, next_state)


    def set_default_transition (self, action, next_state):
        '''This sets the default transition. 
        This defines an action and next_state if the FSM cannot find the
        input symbol and the current state in the transition list and 
        if the FSM cannot find the current_state in the transition_any list.
        This is useful for catching errors and undefined states. 

        The default transition can be removed by setting the attribute
        default_transition to None.
        '''
        self.default_transition = (action, next_state)


    def get_transition (self, input_symbol, state):
        '''This returns (action, next state) given an input_symbol and state.
        This leaves the FSM unchanged. This does not update the current state 
        nor does it trigger the output action. Normally you do not call 
        this method. It is called by process().
        
        The sequence of steps to check for a defined transition goes from 
        the most specific to the least specific. 
        1. Check state_transitions[] that match (input_symbol, state)
        2. Check state_transitions_any[] that match (state)
           In other words, match a specific state and ANY input_symbol.
        3. Check if the default_transition is defined.
           This catches any input_symbol and any state.
           This is a handler for errors, undefined states, or defaults.
        4. No transition was defined. If we get here then raise an exception.
        '''
        if self.state_transitions.has_key((input_symbol, self.current_state)):
            return self.state_transitions[(input_symbol, self.current_state)]
        elif self.state_transitions_any.has_key (self.current_state):
            return self.state_transitions_any[self.current_state]
        elif self.default_transition != None:
            return self.default_transition
        else:
            raise ExceptionFSM ('Transition is undefined: (%s, %s).' % 
                (str(input_symbol), str(self.current_state)) )


    def process (self, input_symbol):
        '''This is the main method that you call to process input.
        This may cause the FSM to change state and call an action.
        This method calls get_transition() to find the action and next_state
        associated with the input_symbol and current_state.
        If the action is None then the action is not called and
        only the current state is changed.
        This method processes one input symbol. You can process a list of
        symbols (or a string) by calling process_list().
        '''
        self.input_symbol = input_symbol
        (action, next_state) = self.get_transition (self.input_symbol, self.current_state)
        if action != None:
            self.callable(action)
        self.current_state = next_state


    def process_list (self, s):
        '''This takes a list and sends each element to process().
        The list may be a string.
        '''
        for c in s:
            self.process (c)
