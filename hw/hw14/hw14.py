import gymnasium as gym
env = gym.make("CartPole-v1", render_mode="human") # 若改用這個，會畫圖
# env = gym.make("CartPole-v1", render_mode="rgb_array")
observation, info = env.reset(seed = 42)
steps = 0
# action[0] = Push cart to the left
# action[1] = Push cart to the right
# Observation[0] = Cart Position
# Observation[1] = Cart Velocity
# Observation[2] = Pole Angle
# Observation[3] = Pole Angular Velocity
for _ in range(1000):
    env.render()
    if observation[2] > 0.01 :
        # action = env.action_space.sample()  # 把這裡改成你的公式，看看能撐多久
        if observation[3] > 0 :
            action = 1
            observation, reward, terminated, truncated, info = env.step(action)
            steps += 1
            observation, reward, terminated, truncated, info = env.step(action)
            steps += 1
        else : 
            action = 0
            observation, reward, terminated, truncated, info = env.step(action)
            steps += 1
    else : 
        if observation[3] < 0 :
            action = 0
            observation, reward, terminated, truncated, info = env.step(action)
            steps += 1
            observation, reward, terminated, truncated, info = env.step(action)
            steps += 1
        else : 
            action = 1
            observation, reward, terminated, truncated, info = env.step(action)
            steps += 1

    if terminated or truncated : # 這裡要加入程式，紀錄你每次撐多久
        observation, info = env.reset()
        print(f"steps: {steps}\n ")
        steps = 0
env.close()