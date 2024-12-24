
def print_bytes(byte_string: bytes) -> None:
    print(r'\x' + r'\x'.join(f'{b:02x}' for b in byte_string))
