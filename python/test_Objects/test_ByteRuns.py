
import Objects

br0 = Objects.ByteRun()
br0.img_offset = 0
br0.len = 20

br1 = Objects.ByteRun()
br1.img_offset = 20
br1.len = 30

br2 = Objects.ByteRun()
br2.img_offset = 50
br2.len = 20


brs_contiguous = Objects.ByteRuns()
brs_contiguous.append(br0)
brs_contiguous.append(br1)
brs_contiguous.append(br2)

brs_glommed = Objects.ByteRuns()
brs_glommed.glom(br0)
brs_glommed.glom(br1)
brs_glommed.glom(br2)

brs_discontig = Objects.ByteRuns()
brs_discontig.glom(br0)
brs_discontig.glom(br2)

assert len(brs_contiguous) == 3
assert len(brs_glommed) == 1
assert len(brs_discontig) == 2
