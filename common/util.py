
def printBytes(byteString: bytes) -> None:
	print(r'\x' + r'\x'.join(f'{b:02x}' for b in byteString))
