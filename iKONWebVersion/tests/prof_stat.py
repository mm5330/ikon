import pstats
import os
dir_path = os.path.dirname(os.path.realpath(__file__))


with open(dir_path + "/prof_out.txt", 'w') as stream:
    stats = pstats.Stats('./POST.button.3642ms.1608407145.prof', stream=stream)
    stats.sort_stats('time', 'calls')
    stats.print_stats()
    stats.print_callers()
