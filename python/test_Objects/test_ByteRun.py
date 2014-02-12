
import Objects
import copy

br1 = Objects.ByteRun()
br1.img_offset = 512
br1.len = 20

br2 = copy.deepcopy(br1)

assert br1 + br2 is None

br2.img_offset += br1.len

assert (br1 + br2).len == 40
