"""
Module containing the different search policies to find the maximum number
of contacts
"""


from __future__ import annotations

import src.encode


def binary_search_policy(seq_file: str, dim: int, ver: int, use_cached: bool, solver: str, count_encoding: str = None) -> dict[str, float]:
    """Binary search for max contacts"""
    total_encode_time, total_solve_time, sat_solve_time = 0.0, 0.0, 0.0
    lo, hi = 0, src.encode.get_max_contacts(
        src.encode.get_sequence(seq_file), dim)
    print(f"Start binary search to max contacts from hi: {hi}")
    while lo <= hi:
        curr = (hi + lo) // 2
        print(f"Solving {curr}:", end=" ", flush=True)
        encode_time, solve_time = src.encode.solve_sat(
            seq_file, curr, dim, ver, use_cached, solver, count_encoding)
        total_encode_time += abs(encode_time)
        total_solve_time += abs(solve_time)
        sat = solve_time > 0
        if sat:
            lo = curr + 1
            sat_solve_time += solve_time
        else:
            curr -= 1
            hi = curr
    print()
    return {
        "max_contacts": curr,
        "encode_time": total_encode_time,
        "solve_time": total_solve_time,
        "sat_solve_time": sat_solve_time
    }


def linear_search_policy(seq_file: str, dim: int, ver: int, use_cached: bool, solver: str, count_encoding: str = None) -> dict[str, float]:
    """Linear search for max contacts"""
    total_encode_time, total_solve_time, sat_solve_time = 0.0, 0.0, 0.0
    curr, max_contacts = 1, src.encode.get_max_contacts(
        src.encode.get_sequence(seq_file), dim)
    print(f"Start linear search to max contacts: {max_contacts}")
    while curr < max_contacts:
        curr += 1
        print(f"Solving {curr}:", end=" ", flush=True)
        encode_time, solve_time = src.encode.solve_sat(
            seq_file, curr, dim, ver, use_cached, solver, count_encoding)
        total_encode_time += abs(encode_time)
        total_solve_time += abs(solve_time)
        sat = solve_time > 0
        if not sat:
            curr -= 1
            break
        sat_solve_time += solve_time
    print()
    return {
        "max_contacts": curr,
        "encode_time": total_encode_time,
        "solve_time": total_solve_time,
        "sat_solve_time": sat_solve_time
    }


def double_binary_policy(seq_file: str, dim: int, ver: int, use_cached: bool, solver: str, count_encoding: str = None) -> dict[str, float]:
    """
    Start the contacts at 1 doubling until unsolvable. Then binary search for the max solvable
    """
    curr = 1
    max_contacts = src.encode.get_max_contacts(
        src.encode.get_sequence(seq_file), dim)
    total_encode_time, total_solve_time, sat_solve_time = 0.0, 0.0, 0.0
    print(f"Start doubling until max contacts: {max_contacts}")
    while curr <= max_contacts:
        print(f"Solving {curr}: ", end="", flush=True)
        encode_time, solve_time = src.encode.solve_sat(
            seq_file, curr, dim, ver, use_cached, solver, count_encoding)
        total_encode_time += abs(encode_time)
        total_solve_time += abs(solve_time)
        sat = solve_time > 0
        if not sat:
            break
        sat_solve_time += solve_time
        curr *= 2
    print(f"Failed to solve at {curr}\n")

    curr -= 1
    lo, hi = curr // 2 + 1, curr
    print("Start binary search to max contacts")
    while lo <= hi:
        curr = (hi + lo) // 2
        print(f"Solving {curr}:", end=" ")
        encode_time, solve_time = src.encode.solve_sat(
            seq_file, curr, dim, ver, use_cached, solver, count_encoding)
        total_encode_time += abs(encode_time)
        total_solve_time += abs(solve_time)
        sat = solve_time > 0
        if sat:
            lo = curr + 1
            sat_solve_time += solve_time
        else:
            curr -= 1
            hi = curr
    print()
    return {
        "max_contacts": curr,
        "encode_time": total_encode_time,
        "solve_time": total_solve_time,
        "sat_solve_time": sat_solve_time
    }


def double_linear_policy(seq_file: str, dim: int, ver: int, use_cached: bool, solver: str, count_encoding: str = None) -> dict[str, float]:
    """Double till UNSAT, then linear search for max contacts"""
    curr = 1
    max_contacts = src.encode.get_max_contacts(
        src.encode.get_sequence(seq_file), dim)
    total_encode_time, total_solve_time, sat_solve_time = 0.0, 0.0, 0.0
    print(f"Start doubling until max contacts: {max_contacts}")
    while curr <= max_contacts:
        print(f"Solving {curr}: ", end="", flush=True)
        encode_time, solve_time = src.encode.solve_sat(
            seq_file, curr, dim, ver, use_cached, solver, count_encoding)
        total_encode_time += abs(encode_time)
        total_solve_time += abs(solve_time)
        sat = solve_time > 0
        if not sat:
            break
        sat_solve_time += solve_time
        curr *= 2
    print(f"Failed to solve at {curr}\n")

    curr = curr // 2 - 1
    print("Start linear search to max contacts")
    while curr < max_contacts:
        curr += 1
        print(f"Solving {curr}:", end=" ", flush=True)
        encode_time, solve_time = src.encode.solve_sat(
            seq_file, curr, dim, ver, use_cached, solver, count_encoding)
        total_encode_time += abs(encode_time)
        total_solve_time += abs(solve_time)
        sat = solve_time > 0
        if not sat:
            curr -= 1
            break
        sat_solve_time += solve_time
    print()
    return {
        "max_contacts": curr,
        "encode_time": total_encode_time,
        "solve_time": total_solve_time,
        "sat_solve_time": sat_solve_time
    }
