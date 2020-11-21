from __future__ import annotations

from typing import List



def quicksort (array : List[int]) -> List[int]:
	if len (array) <= 1:
		return array
	p, i, j = 0, 0, len(array)-1
	while i < j:
		if i == p:
			if array[p] > array[j]:
				array[j] += array[p]
				array[p] = array[j] - array[p]
				array[j] -= array[p]
				p = j
			else:
				j -= 1
		if j == p:
			if array[p] < array[i]:
				array[i] += array[p]
				array[p] = array[i] - array[p]
				array[i] -= array[p]
				p = i
			else:
				i += 1
	return quicksort(array[:p]) + [array[p]] + quicksort(array[p+1:])
