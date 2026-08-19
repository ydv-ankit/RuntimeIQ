local owner = redis.call("HGET", KEYS[1], ARGV[1])

if owner ~= ARGV[2] then
    return 0
end

redis.call("ZADD", KEYS[2], ARGV[3], ARGV[1])

return 1