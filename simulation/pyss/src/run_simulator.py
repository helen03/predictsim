#! /usr/bin/env python2

import sys
if __debug__:
    import warnings
    #warnings.warn("Running in debug mode, this will be slow... try 'python2.4 -O %s'" % sys.argv[0])

from base.workload_parser import parse_lines
from base.prototype import _job_inputs_to_jobs
from schedulers.simulator import run_simulator
import optparse
import schedulers.common_correctors


def module_to_class(module):
	"""
	transform foo_bar to FooBar
	"""
	return ''.join(w.title() for w in str.split(module, "_"))


def parse_options():
    parser = optparse.OptionParser()
    parser.add_option("--num-processors", type="int", \
                      help="the number of available processors in the simulated parallel machine")
    parser.add_option("--input-file", \
                      help="a file in the standard workload format: http://www.cs.huji.ac.il/labs/parallel/workload/swf.html, if '-' read from stdin")
    parser.add_option("--scheduler", 
                      help="The scheduler to use. To list them: for s in schedulers/*_scheduler.py ; do basename -s .py $s; done")
    parser.add_option("--predictor", 
                      help="The predictor (if needed) to use. To list them: for s in predictors/predictor_*.py ; do basename -s .py $s; done")
    parser.add_option("--corrector", 
                      help="The corrector (if needed) to use. Choose between: "+str(schedulers.common_correctors.correctors_list()))
    parser.add_option("--output-swf", type="string", \
                      help="if set, create a swf file of the run")
    parser.add_option("--no-stats", action="store_true", dest="no_stats", \
                      help="if set, no stats will be computed")
    
    options, args = parser.parse_args()

    if options.input_file is None:
        parser.error("missing input file")

    if options.num_processors is None:
	input_file = open(options.input_file)
        for line in input_file:
		if(line.lstrip().startswith(';')):
			if(line.lstrip().startswith('; MaxProcs:')):
				options.num_processors = int(line.strip()[11:])
				break
			else:
				continue
		else:
			break
	if options.num_processors is None:
		parser.error("missing num processors")

    if options.scheduler is None:
         parser.error("missing scheduler")
         
    if options.no_stats is None:
	    options.no_stats = False

    if args:
        parser.error("unknown extra arguments: %s" % args)

    return options

def main():
    options = parse_options()

    if options.input_file == "-":
        input_file = sys.stdin
    else:
        input_file = open(options.input_file)

    my_module = options.scheduler
    my_class = module_to_class(my_module)

    #load module(or file)
    package = __import__ ('schedulers', fromlist=[my_module])
    if my_module not in package.__dict__:
        print "No such scheduler (module file not found)."
        return 
    if my_class not in package.__dict__[my_module].__dict__:
        print "No such scheduler (class within the module file not found)."
        return
    #load the class
    scheduler_non_instancied = package.__dict__[my_module].__dict__[my_class]

    if hasattr(scheduler_non_instancied, 'I_NEED_A_PREDICTOR'):
        my_module = options.predictor
        print(my_module)
        if my_module is None:
            print("This scheduler need a predictor")
            return
        my_class = module_to_class(my_module) 
        package = __import__ ('predictors', fromlist=[my_module])
        if my_module not in package.__dict__:
            print "No such predictor (module file not found)."
            return 
        if my_class not in package.__dict__[my_module].__dict__:
            print "No such predictor (class within the module file not found)."
            return
        #load the class
        predictor = package.__dict__[my_module].__dict__[my_class](options.num_processors)
        
        #now the corrector
        #if options.corrector is None:
		#print("This scheduler need a corrector")
		#return
	
	
	
        scheduler = scheduler_non_instancied(options.num_processors, predictor)
    else:
        scheduler = scheduler_non_instancied(options.num_processors)

    try:
        print "...." 
        run_simulator(
                num_processors = options.num_processors, 
                jobs = _job_inputs_to_jobs(parse_lines(input_file), options.num_processors),
                scheduler = scheduler,
                output_swf = options.output_swf,
                input_file = options.input_file,
                no_stats = options.no_stats
            )
        
        print "Num of Processors: ", options.num_processors
        print "Input file: ", options.input_file
        print "Scheduler:", type(scheduler)

    finally:
        if input_file is not sys.stdin:
            input_file.close()


main()
