import struct, zlib, math

class png_obj:
	def __init__(self, png_file):
		# Read file
		f = open(png_file, 'rb')
		self.raw_data = f.read()

		# Check first 8 bytes for PNG header
		header_arr = self.raw_data[0:8]
		header_int_arr = bytes([137, 80, 78, 71, 13, 10, 26, 10])
		header_byte_arr = bytearray(header_int_arr)
		if header_arr != header_int_arr:
			raise Exception("PNG Object can only read PNGs. Header bytes mismatch")

		# IHDR Length/header
		IHDR_leng_raw = self.raw_data[8:12]
		IHDR_leng_dc = int.from_bytes(IHDR_leng_raw, byteorder='big')

		IHDR_name_raw = self.raw_data[12:16]
		IHDR_name_dc = IHDR_name_raw.decode('ascii')

		# IHDR values
		width_raw = self.raw_data[16:20]
		self.width_dc = int.from_bytes(width_raw, byteorder='big')

		height_raw = self.raw_data[20:24]
		self.height_dc = int.from_bytes(height_raw, byteorder='big')

		self.bit_depth = self.raw_data[24]
		self.color_type = self.raw_data[25]
		self.compression_method = self.raw_data[26]
		self.filter_method = self.raw_data[27]
		self.interlace = self.raw_data[28]

		# Read all other chunks
		i = 33
		self.chunks_in_file = ["IHDR"]
		self.red_arr = []
		self.green_arr = []
		self.blue_arr = []
		self.alpha_arr = []

		while i < len(self.raw_data):
			chunk_length_raw = self.raw_data[i:i+4]
			chunk_length_dc = int.from_bytes(chunk_length_raw, byteorder='big')
			i += 4
			chunk_name_raw = self.raw_data[i:i+4]
			chunk_name_dc = chunk_name_raw.decode('ascii')

			self.chunks_in_file.append(chunk_name_dc)

			# IDAT Section
			if chunk_name_dc == "IDAT":
				compressed_idat = self.raw_data[i+4:i+4+chunk_length_dc]
				idat_data = zlib.decompress(compressed_idat)
				j = 0
				column = 0
				cur_filter = -1
				cur_pixel = 0
				first_line = True

				if self.color_type == 6:
					while j < len(idat_data):
						if column == 0:
							cur_filter = idat_data[j]
							j += 1
						if cur_filter == 0:
							self.red_arr.append(idat_data[j])
							self.green_arr.append(idat_data[j+1])
							self.blue_arr.append(idat_data[j+2])
							self.alpha_arr.append(idat_data[j+3])
						elif cur_filter == 1 and len(self.red_arr) != 0:
							if idat_data[j] + self.red_arr[cur_pixel - 1] < 256:
								self.red_arr.append(idat_data[j] + self.red_arr[cur_pixel - 1])
							else:
								self.red_arr.append(idat_data[j] + self.red_arr[cur_pixel - 1] - 256)
							if idat_data[j+1] + self.green_arr[cur_pixel - 1] < 256:
								self.green_arr.append(idat_data[j+1] + self.green_arr[cur_pixel - 1])
							else:
								self.green_arr.append(idat_data[j+1] + self.green_arr[cur_pixel - 1] - 256)
							if idat_data[j+2] + self.blue_arr[cur_pixel - 1] < 256:
								self.blue_arr.append(idat_data[j+2] + self.blue_arr[cur_pixel - 1])
							else:
								self.blue_arr.append(idat_data[j+2] + self.blue_arr[cur_pixel - 1] - 256)
							if idat_data[j+3] + self.alpha_arr[cur_pixel - 1] < 256:
								self.alpha_arr.append(idat_data[j+3] + self.alpha_arr[cur_pixel - 1])
							else:
								self.alpha_arr.append(idat_data[j+3] + self.alpha_arr[cur_pixel - 1] - 256)
						elif cur_filter == 1 and len(self.red_arr) == 0:
							self.red_arr.append(idat_data[j])
							self.green_arr.append(idat_data[j+1])
							self.blue_arr.append(idat_data[j+2])
							self.alpha_arr.append(idat_data[j+3])
						elif cur_filter == 2 and not first_line:
							if idat_data[j] + self.red_arr[cur_pixel - self.width_dc] < 256:
								self.red_arr.append(idat_data[j] + self.red_arr[cur_pixel - self.width_dc])
							else:
								self.red_arr.append(idat_data[j] + self.red_arr[cur_pixel - self.width_dc] - 256)
							if idat_data[j+1] + self.green_arr[cur_pixel - self.width_dc] < 256:
								self.green_arr.append(idat_data[j+1] + self.green_arr[cur_pixel - self.width_dc])
							else:
								self.green_arr.append(idat_data[j+1] + self.green_arr[cur_pixel - self.width_dc] - 256)
							if idat_data[j+2] + self.blue_arr[cur_pixel - self.width_dc] < 256:
								self.blue_arr.append(idat_data[j+2] + self.blue_arr[cur_pixel - self.width_dc])
							else:
								self.blue_arr.append(idat_data[j+2] + self.blue_arr[cur_pixel - self.width_dc] - 256)
							if idat_data[j+3] + self.alpha_arr[cur_pixel - self.width_dc] < 256:
								self.alpha_arr.append(idat_data[j+3] + self.alpha_arr[cur_pixel - self.width_dc])
							else:
								self.alpha_arr.append(idat_data[j+3] + self.alpha_arr[cur_pixel - self.width_dc] - 256)
						elif cur_filter == 2 and first_line:
							self.red_arr.append(idat_data[j])
							self.green_arr.append(idat_data[j+1])
							self.blue_arr.append(idat_data[j+2])
							self.alpha_arr.append(idat_data[j+3])
						elif cur_filter == 3 and not first_line:
							average = (self.red_arr[cur_pixel - 1] + self.red_arr[cur_pixel - self.width_dc])/2
							average = math.floor(average)
							if idat_data[j] + average < 256:
								self.red_arr.append(idat_data[j] + average)
							else:
								self.red_arr.append(idat_data[j] + average - 256)
							average = (self.green_arr[cur_pixel - 1] + self.green_arr[cur_pixel - self.width_dc])/2
							average = math.floor(average)
							if idat_data[j+1] + average < 256:
								self.green_arr.append(idat_data[j+1] + average)
							else:
								self.green_arr.append(idat_data[j+1] + average - 256)
							average = (self.blue_arr[cur_pixel - 1] + self.blue_arr[cur_pixel - self.width_dc])/2
							average = math.floor(average)
							if idat_data[j+2] + average < 256:
								self.blue_arr.append(idat_data[j+2] + average)
							else:
								self.blue_arr.append(idat_data[j+2] + average - 256)
							average = (self.alpha_arr[cur_pixel - 1] + self.alpha_arr[cur_pixel - self.width_dc])/2
							average = math.floor(average)
							if idat_data[j+3] + average < 256:
								self.alpha_arr.append(idat_data[j+3] + average)
							else:
								self.alpha_arr.append(idat_data[j+3] + average - 256)
						elif cur_filter == 3 and first_line:
							self.red_arr.append(idat_data[j])
							self.green_arr.append(idat_data[j+1])
							self.blue_arr.append(idat_data[j+2])
							self.alpha_arr.append(idat_data[j+3])
						elif cur_filter == 4 and not first_line:
							pix_a = self.red_arr[cur_pixel - 1]
							pix_b = self.red_arr[cur_pixel - self.width_dc]
							pix_c = self.red_arr[cur_pixel - self.width_dc - 1]
							paeth = pix_a + pix_b - pix_c
							paeth_a = abs(paeth - pix_a)
							paeth_b = abs(paeth - pix_b)
							paeth_c = abs(paeth - pix_c)
							if paeth_a <= paeth_b and paeth_a <= paeth_c:
								paeth_r = pix_a
							elif paeth_b <= paeth_c:
								paeth_r = pix_b
							else:
								paeth_r = pix_c
							if idat_data[j] + paeth_r < 256:
								self.red_arr.append(idat_data[j] + paeth_r)
							else:
								self.red_arr.append(idat_data[j] + paeth_r - 256)

							pix_a = self.green_arr[cur_pixel - 1]
							pix_b = self.green_arr[cur_pixel - self.width_dc]
							pix_c = self.green_arr[cur_pixel - self.width_dc - 1]
							paeth = pix_a + pix_b - pix_c
							paeth_a = abs(paeth - pix_a)
							paeth_b = abs(paeth - pix_b)
							paeth_c = abs(paeth - pix_c)
							if paeth_a <= paeth_b and paeth_a <= paeth_c:
								paeth_r = pix_a
							elif paeth_b <= paeth_c:
								paeth_r = pix_b
							else:
								paeth_r = pix_c
							if idat_data[j+1] + paeth_r < 256:
								self.green_arr.append(idat_data[j+1] + paeth_r)
							else:
								self.green_arr.append(idat_data[j+1] + paeth_r - 256)

							pix_a = self.blue_arr[cur_pixel - 1]
							pix_b = self.blue_arr[cur_pixel - self.width_dc]
							pix_c = self.blue_arr[cur_pixel - self.width_dc - 1]
							paeth = pix_a + pix_b - pix_c
							paeth_a = abs(paeth - pix_a)
							paeth_b = abs(paeth - pix_b)
							paeth_c = abs(paeth - pix_c)
							if paeth_a <= paeth_b and paeth_a <= paeth_c:
								paeth_r = pix_a
							elif paeth_b <= paeth_c:
								paeth_r = pix_b
							else:
								paeth_r = pix_c
							if idat_data[j+2] + paeth_r < 256:
								self.blue_arr.append(idat_data[j+2] + paeth_r)
							else:
								self.blue_arr.append(idat_data[j+2] + paeth_r - 256)

							pix_a = self.alpha_arr[cur_pixel - 1]
							pix_b = self.alpha_arr[cur_pixel - self.width_dc]
							pix_c = self.alpha_arr[cur_pixel - self.width_dc - 1]
							paeth = pix_a + pix_b - pix_c
							paeth_a = abs(paeth - pix_a)
							paeth_b = abs(paeth - pix_b)
							paeth_c = abs(paeth - pix_c)
							if paeth_a <= paeth_b and paeth_a <= paeth_c:
								paeth_r = pix_a
							elif paeth_b <= paeth_c:
								paeth_r = pix_b
							else:
								paeth_r = pix_c
							if idat_data[j+3] + paeth_r < 256:
								self.alpha_arr.append(idat_data[j+3] + paeth_r)
							else:
								self.alpha_arr.append(idat_data[j+3] + paeth_r - 256)
						elif cur_filter == 4 and first_line:
							self.red_arr.append(idat_data[j])
							self.green_arr.append(idat_data[j+1])
							self.blue_arr.append(idat_data[j+2])
							self.alpha_arr.append(idat_data[j+3])
						j += 4
						cur_pixel += 1
						if column == self.width_dc - 1:
							column = 0
							first_line = False
						else:
							column += 1


			if chunk_name_dc == "IEND":
				i += 20
			else:
				i += 8 + chunk_length_dc



	def PrintHeaderValues(self):
		print("Width:", self.width_dc)
		print("Height:", self.height_dc)
		print("Bit depth:", self.bit_depth)
		if self.color_type == 0:
			print("Color type: Greyscale (0)")
		elif self.color_type == 2:
			print("Color type: Truecolor (2)")
		elif self.color_type == 3:
			print("Color type: Indexed-color (3)")
		elif self.color_type == 4:
			print("Color type: Greyscale with Alpha (4)")
		elif self.color_type == 6:
			print("Color type: Truecolor with Alpha (6)")
		print("Compression method:", self.compression_method)
		print("Filter method:", self.filter_method)
		print("Interlace:", self.interlace)


	def PrintChunks(self):
		j = 0
		while j < len(self.chunks_in_file):
			print("Chunk " + str(j+1) + ": " + self.chunks_in_file[j])
			j += 1

	def PrintPixels(self):
		j = 0
		while j < len(self.red_arr):
			print("Pixel " + str(j+1) + ": " + str(self.red_arr[j]) + " " + str(self.green_arr[j]) + " " + str(self.blue_arr[j]) + " " + str(self.alpha_arr[j]))
			j += 1


img = png_obj("test3.png")
img.PrintHeaderValues()
img.PrintPixels()
