import urllib.request as u, json, os, sys, time
E = os.environ.get
U = E("MAKEFUN_ENV_URL")
def post(p, o):
    r = u.Request(U + p, json.dumps(o).encode(), {"Content-Type": "application/json"})
    with u.urlopen(r) as f:
        return json.loads(f.read())
V = [0, 100, 320, 330, 500, 900, 20000]
INF = 10 ** 9
OK = [i for i in range(128) if not (i & 0x88)]
NODES = [0]
BUDGET = 36000
def sq(s):
    return (8 - int(s[1])) * 16 + (ord(s[0]) - 97)
def name(i):
    return "abcdefgh"[i & 7] + str(8 - (i >> 4))
def parse(fen):
    parts = fen.split()
    board = [0] * 128
    for r, row in enumerate(parts[0].split("/")):
        f = 0
        for ch in row:
            if ch.isdigit():
                f += int(ch)
            else:
                j = "PNBRQKpnbrqk".index(ch)
                pc = j % 6 + 1
                board[r * 16 + f] = pc if j < 6 else -pc
                f += 1
    rights = 0
    for k, v in (("K", 1), ("Q", 2), ("k", 4), ("q", 8)):
        if k in parts[2]:
            rights |= v
    ep = -1 if parts[3] == "-" else sq(parts[3])
    return board, 0 if parts[1] == "w" else 1, rights, ep
def attacked(board, target, side):
    if side == 0:
        t = target + 15
        if 0 <= t < 128 and not (t & 0x88) and board[t] == 1:
            return 1
        t = target + 17
        if 0 <= t < 128 and not (t & 0x88) and board[t] == 1:
            return 1
        sgn, kn, bq, rq, kq = 1, 2, 3, 4, 5
    else:
        t = target - 15
        if 0 <= t < 128 and not (t & 0x88) and board[t] == -1:
            return 1
        t = target - 17
        if 0 <= t < 128 and not (t & 0x88) and board[t] == -1:
            return 1
        sgn, kn, bq, rq, kq = -1, -2, -3, -4, -5
    for d in (-33, -31, -18, -14, 14, 18, 31, 33):
        t = target + d
        if 0 <= t < 128 and not (t & 0x88):
            p = board[t]
            if p and (p if p > 0 else -p) == 2 and p == kn:
                return 1
    for d in (-17, -15, 15, 17):
        t = target + d
        first = 1
        while 0 <= t < 128 and not (t & 0x88):
            p = board[t]
            if p:
                if (p == bq or p == kq) or (p == (6 * sgn) and first):
                    return 1
                break
            first = 0
            t += d
    for d in (-16, -1, 1, 16):
        t = target + d
        first = 1
        while 0 <= t < 128 and not (t & 0x88):
            p = board[t]
            if p:
                if (p == rq or p == kq) or (p == (6 * sgn) and first):
                    return 1
                break
            first = 0
            t += d
    return 0
def in_check(board, side):
    king = 6 if side == 0 else -6
    for i in OK:
        if board[i] == king:
            return attacked(board, i, 1 - side)
    return 0
def mk(board, side, rights, ep, m):
    b = board[:]
    f, t, promo = m
    p = b[f]
    b[f] = 0
    b[t] = p
    nr = rights
    nep = -1
    if p == 6:
        nr &= ~3
    if p == -6:
        nr &= ~12
    if f == 112 or t == 112:
        nr &= ~2
    if f == 119 or t == 119:
        nr &= ~1
    if f == 0 or t == 0:
        nr &= ~8
    if f == 7 or t == 7:
        nr &= ~4
    if abs(p) == 1 and t == ep and ep != -1:
        b[t + (16 if side == 0 else -16)] = 0
    if p == 1 and f - t == 32:
        nep = f - 16
    if p == -1 and t - f == 32:
        nep = f + 16
    if promo:
        b[t] = promo if side == 0 else -promo
    if p == 6 and f == 116:
        if t == 118:
            b[119] = 0
            b[117] = 4
        if t == 114:
            b[112] = 0
            b[115] = 4
    if p == -6 and f == 4:
        if t == 6:
            b[7] = 0
            b[5] = -4
        if t == 2:
            b[0] = 0
            b[3] = -4
    return b, 1 - side, nr, nep
def make_inplace(board, side, ep, m):
    f, t, promo = m
    p = board[f]
    cap = board[t]
    board[f] = 0
    board[t] = (promo if p > 0 else -promo) if promo else p
    epsq = -1
    if abs(p) == 1 and t == ep:
        epsq = t + (16 if side == 0 else -16)
        board[epsq] = 0
    return (cap, epsq)
def unmake_inplace(board, side, m, u):
    f, t, promo = m
    p = board[t]
    if promo:
        p = 1 if p > 0 else -1
    board[f] = p
    board[t] = u[0]
    if u[1] >= 0:
        board[u[1]] = -1 if side == 0 else 1
def gen(board, side, rights, ep):
    moves = []
    mine = lambda p: (p > 0) == (side == 0)
    for i in range(128):
        if i & 0x88:
            continue
        p = board[i]
        if not p or not mine(p):
            continue
        ap = abs(p)
        if ap == 1:
            d = -16 if side == 0 else 16
            start_rank = 6 if side == 0 else 1
            promo_rank = 0 if side == 0 else 7
            t = i + d
            if not (t & 0x88) and board[t] == 0:
                if (t >> 4) == promo_rank:
                    for pr in (5, 4, 3, 2):
                        moves.append((i, t, pr))
                else:
                    moves.append((i, t, 0))
                    if (i >> 4) == start_rank and board[i + 2 * d] == 0:
                        moves.append((i, i + 2 * d, 0))
            for dc in (-1, 1):
                t = i + d + dc
                if t & 0x88:
                    continue
                if (board[t] and not mine(board[t])) or t == ep:
                    if (t >> 4) == promo_rank:
                        for pr in (5, 4, 3, 2):
                            moves.append((i, t, pr))
                    else:
                        moves.append((i, t, 0))
        elif ap == 2:
            for d in (-33, -31, -18, -14, 14, 18, 31, 33):
                t = i + d
                if not (t & 0x88) and (board[t] == 0 or not mine(board[t])):
                    moves.append((i, t, 0))
        elif ap == 6:
            for d in (-17, -15, 15, 17, -16, -1, 1, 16):
                t = i + d
                if not (t & 0x88) and (board[t] == 0 or not mine(board[t])):
                    moves.append((i, t, 0))
        else:
            dirs = []
            if ap in (3, 5):
                dirs += (-17, -15, 15, 17)
            if ap in (4, 5):
                dirs += (-16, -1, 1, 16)
            for d in dirs:
                t = i + d
                while not (t & 0x88):
                    if board[t] == 0:
                        moves.append((i, t, 0))
                    else:
                        if not mine(board[t]):
                            moves.append((i, t, 0))
                        break
                    t += d
    if side == 0:
        if rights & 1 and board[116] == 6 and board[117] == 0 == board[118] and board[119] == 4 \
                and not attacked(board, 116, 1) and not attacked(board, 117, 1) and not attacked(board, 118, 1):
            moves.append((116, 118, 0))
        if rights & 2 and board[116] == 6 and board[115] == 0 == board[114] == board[113] and board[112] == 4 \
                and not attacked(board, 116, 1) and not attacked(board, 115, 1) and not attacked(board, 114, 1):
            moves.append((116, 114, 0))
    else:
        if rights & 4 and board[4] == -6 and board[5] == 0 == board[6] and board[7] == -4 \
                and not attacked(board, 4, 0) and not attacked(board, 5, 0) and not attacked(board, 6, 0):
            moves.append((4, 6, 0))
        if rights & 8 and board[4] == -6 and board[3] == 0 == board[2] == board[1] and board[0] == -4 \
                and not attacked(board, 4, 0) and not attacked(board, 3, 0) and not attacked(board, 2, 0):
            moves.append((4, 2, 0))
    out = []
    for m in moves:
        u = make_inplace(board, side, ep, m)
        ok = not in_check(board, side)
        unmake_inplace(board, side, m, u)
        if ok:
            out.append(m)
    return out
def uci(m):
    s = name(m[0]) + name(m[1])
    return s + (" nbrq"[m[2]] if 0 < m[2] < 5 else "")
def ev(board, side=0):
    sc = 0
    wk = bk = 0
    wb = bb = 0
    wpf = [0] * 8
    bpf = [0] * 8
    for i in OK:
        q = board[i]
        if q == 3:
            wb += 1
        elif q == -3:
            bb += 1
        elif q == 1:
            wpf[i & 7] += 1
        elif q == -1:
            bpf[i & 7] += 1
    for i in OK:
        p = board[i]
        if not p:
            continue
        ap = abs(p)
        r = i >> 4
        f = i & 7
        rr = r if p < 0 else 7 - r
        home = 0
        v = V[ap]
        if ap == 1:
            v += rr * 3
            if f in (3, 4):
                v += 10
            elif 2 <= f <= 5:
                v += 4
        elif ap == 6:
            wk = i if p > 0 else wk
            bk = i if p < 0 else bk
            if 4 <= f <= 6 and rr >= 6:
                v += 30
        else:
            v += (3 - abs(3 - f) - abs(3 - rr)) * 6
            if ap in (2, 3) and rr != home:
                v += 55
            me = 0 if p > 0 else 1
            if attacked(board, i, 1 - me) and not attacked(board, i, me):
                v = v // 2
        sc += v if p > 0 else -v
    if wk:
        n = 0
        for d in (-17, -16, -15, -1, 1, 15, 16, 17):
            t = wk + d
            if t in OK and board[t] and board[t] > 0 and abs(board[t]) in (1, 2, 3):
                n += 1
        sc += n * 6
    if bk:
        n = 0
        for d in (-17, -16, -15, -1, 1, 15, 16, 17):
            t = bk + d
            if t in OK and board[t] and board[t] < 0 and abs(board[t]) in (1, 2, 3):
                n += 1
        sc -= n * 6
    if wb >= 2:
        sc += 30
    if bb >= 2:
        sc -= 30
    for f in range(8):
        if wpf[f] > 1:
            sc -= 14 * (wpf[f] - 1)
        if bpf[f] > 1:
            sc += 14 * (bpf[f] - 1)
        near_w = wpf[f - 1] if f else 0
        near_w += wpf[f + 1] if f < 7 else 0
        if wpf[f] and not near_w:
            sc -= 12
        near_b = bpf[f - 1] if f else 0
        near_b += bpf[f + 1] if f < 7 else 0
        if bpf[f] and not near_b:
            sc += 12
    return sc if side == 0 else -sc
def nz(board, side, ep, m):
    return board[m[1]] or m[2] or (abs(board[m[0]]) == 1 and m[1] == ep)
def ok_(board, side, ep, m):
    s = 0
    if board[m[1]]:
        s += 10 * V[abs(board[m[1]])] - V[abs(board[m[0]])]
    if m[2]:
        s += 800
    if abs(board[m[0]]) == 1 and m[1] == ep:
        s += 100
    return s
def qs(board, side, rights, ep, alpha, beta, qd=0):
    NODES[0] += 1
    stand = ev(board, side)
    if stand >= beta:
        return beta
    if stand > alpha:
        alpha = stand
    if qd >= 4 or NODES[0] > BUDGET * 3 // 2:
        return alpha
    moves = [m for m in gen(board, side, rights, ep) if nz(board, side, ep, m)]
    if not moves:
        return alpha
    moves.sort(key=lambda m: -ok_(board, side, ep, m))
    for m in moves:
        b2, nt, nr, nep = mk(board, side, rights, ep, m)
        sc = -qs(b2, nt, nr, nep, -beta, -alpha, qd + 1)
        if sc >= beta:
            return beta
        if sc > alpha:
            alpha = sc
    return alpha
KL = {}
def search(board, side, rights, ep, depth, alpha, beta, ply=0):
    NODES[0] += 1
    if NODES[0] > BUDGET * 3 // 2:
        return qs(board, side, rights, ep, alpha, beta)
    moves = gen(board, side, rights, ep)
    if not moves:
        return (-INF + 50) if in_check(board, side) else 0
    if depth <= 0:
        return qs(board, side, rights, ep, alpha, beta)
    ks = KL.get(ply, 0)
    moves.sort(key=lambda m: (m != ks, -ok_(board, side, ep, m)))
    best = -INF
    first = 1
    for m in moves:
        b2, nt, nr, nep = mk(board, side, rights, ep, m)
        if first:
            sc = -search(b2, nt, nr, nep, depth - 1, -beta, -alpha, ply + 1)
            first = 0
        else:
            sc = -search(b2, nt, nr, nep, depth - 1, -alpha - 1, -alpha, ply + 1)
            if alpha < sc < beta:
                sc = -search(b2, nt, nr, nep, depth - 1, -beta, -alpha, ply + 1)
        if sc > best:
            best = sc
        if sc > alpha:
            alpha = sc
        if alpha >= beta:
            if not nz(board, side, ep, m):
                KL[ply] = m
            break
    return best
def pick(bd, sd, rt, ep, legal):
 NODES[0] = 0
 KL.clear()
 mv = gen(bd, sd, rt, ep)
 if legal:
  ls = set(legal)
  kp = [m for m in mv if uci(m) in ls]
  if kp:
   mv = kp
 if not mv:
  return legal[0] if legal else "0000"
 if len(mv) == 1:
  return uci(mv[0])
 mv.sort(key=lambda m: -ok_(bd, sd, ep, m))
 best = mv[0]
 sc1 = []
 for m in mv:
  b2, nt, nr, nep = mk(bd, sd, rt, ep, m)
  sc1.append((-search(b2, nt, nr, nep, 0, -INF, INF, 1), m))
 sc1.sort(key=lambda t: (-t[0], uci(t[1])))
 mv = [m for _, m in sc1]
 best = mv[0]
 for d in range(2, 9):
  if NODES[0] > BUDGET:
   break
  alpha = -INF
  sc = []
  for m in mv:
   if NODES[0] > BUDGET:
    break
   b2, nt, nr, nep = mk(bd, sd, rt, ep, m)
   v = -search(b2, nt, nr, nep, d - 1, -INF, INF)
   sc.append((v, m))
   if v > alpha:
    alpha = v
  if len(sc) < len(mv):
   break
  sc.sort(key=lambda t: (-t[0], uci(t[1])))
  if sc[0][1] != mv[0]:
   best = sc[0][1]
  else:
   best = sc[0][1]
  mv = [m for _, m in sc]
 return uci(best)
def play():
    game = post("/game", {})
    while 1:
        status = game.get("status")
        if status == "done":
            print(f"done: {game.get('wins')} won, {game.get('draws')} drawn, {game.get('losses')} lost", file=sys.stderr)
            return
        if status == "your_move":
            board, side, rights, ep = parse(game["fen"])
            move = pick(board, side, rights, ep, game.get("legal_moves") or [])
            game = post("/move", {"game": game["game"], "move": move})
        else:
            game = post("/game", {})
if __name__ == "__main__":
    play()