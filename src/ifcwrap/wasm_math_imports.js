addToLibrary({
  acos: 'Math.acos',
  acosh: 'Math.acosh',
  asin: 'Math.asin',
  asinh: 'Math.asinh',
  atan: 'Math.atan',
  atan2: 'Math.atan2',
  atanh: 'Math.atanh',
  cos: 'Math.cos',
  cosh: 'Math.cosh',
  exp: 'Math.exp',
  exp2: function(x) {
    return Math.pow(2, x);
  },
  fmax: function(a, b) {
    if (isNaN(a)) return b;
    if (isNaN(b)) return a;
    return Math.max(a, b);
  },
  fmin: function(a, b) {
    if (isNaN(a)) return b;
    if (isNaN(b)) return a;
    return Math.min(a, b);
  },
  fmod: function(x, y) {
    return x % y;
  },
  ldexp: function(x, exp) {
    return x * Math.pow(2, exp);
  },
  llround: function(x) {
    return x >= 0 ? Math.floor(x + 0.5) : Math.ceil(x - 0.5);
  },
  log: 'Math.log',
  log10: 'Math.log10',
  log2: 'Math.log2',
  lround: function(x) {
    return x >= 0 ? Math.floor(x + 0.5) : Math.ceil(x - 0.5);
  },
  modf: function(x, iptr) {
    var intPart = Math.trunc(x);
    HEAPF64[iptr >> 3] = intPart;
    return x - intPart;
  },
  pow: 'Math.pow',
  remquo: function(x, y, quo) {
    var n = Math.round(x / y);
    HEAP32[quo >> 2] = n;
    return x - n * y;
  },
  round: function(x) {
    return x >= 0 ? Math.floor(x + 0.5) : Math.ceil(x - 0.5);
  },
  sin: 'Math.sin',
  sinh: 'Math.sinh',
  tan: 'Math.tan',
});
