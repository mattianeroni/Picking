import itertools


def quicksort (array):
	"""
	Quicksort algorithm.
	
	"""
	if len (array) <= 1:
		return array
	p, i, j = 0, 0, len(array)-1
	while i < j:
		if i == p:
			if array[p] > array[j]:
				array[j], array[p] = array[p], array[j]
				p = j
			else:
				j -= 1
		if j == p:
			if array[p] < array[i]:
				array[i], array[p] = array[p], array[i]
				p = i
			else:
				i += 1
	return itertools.chain (quicksort(array[:p]), [array[p]], quicksort(array[p+1:]))
