def get_coupon_codes():
    return [['DEAL20']]
(a1,), = get_coupon_codes()
(a2,) = get_coupon_codes()
(a3), = get_coupon_codes()
(a4) = get_coupon_codes()
a5, = get_coupon_codes()
a6 = get_coupon_codes()

print(a1)
print(a2)
print(a3)
print(a4)
print(a5)
print(a6)

assert a1 not in (a2, a3, a4, a5, a6)
assert a2 == a3 == a5
assert a4 == a6