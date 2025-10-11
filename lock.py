# Python GIL 和 Mutex 示例演示

import threading
import time
import concurrent.futures
from threading import Lock, RLock
import multiprocessing
import os

print("🔒 Python GIL 和 Mutex 机制演示")
print("=" * 80)

# 全局变量和锁
counter = 0
counter_lock = Lock()
rlock = RLock()

# 1. GIL 演示：CPU 密集型任务
print("\n📝 1. GIL 演示：CPU 密集型任务")
print("-" * 50)

def cpu_intensive_task(n, task_name):
    """CPU 密集型任务"""
    print(f"开始执行 {task_name} (线程ID: {threading.current_thread().ident})")
    start_time = time.time()
    
    # 模拟 CPU 密集型计算
    result = 0
    for i in range(n):
        result += i ** 2
    
    end_time = time.time()
    print(f"{task_name} 完成，耗时: {end_time - start_time:.3f}秒，结果: {result}")
    return end_time - start_time

def demonstrate_gil():
    """演示 GIL 对 CPU 密集型任务的影响"""
    n = 1000000
    
    print("🔄 单线程执行:")
    start_time = time.time()
    time1 = cpu_intensive_task(n, "任务1")
    time2 = cpu_intensive_task(n, "任务2")
    single_thread_total = time.time() - start_time
    print(f"单线程总耗时: {single_thread_total:.3f}秒\n")
    
    print("🔄 多线程执行 (受 GIL 限制):")
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future1 = executor.submit(cpu_intensive_task, n, "线程任务1")
        future2 = executor.submit(cpu_intensive_task, n, "线程任务2")
        
        future1.result()
        future2.result()
    
    multi_thread_total = time.time() - start_time
    print(f"多线程总耗时: {multi_thread_total:.3f}秒")
    print(f"加速比: {single_thread_total / multi_thread_total:.2f}x")
    
    if multi_thread_total >= single_thread_total * 0.8:
        print("⚠️  GIL 限制了多线程 CPU 密集型任务的性能提升")
    else:
        print("✅ 多线程有明显性能提升")

demonstrate_gil()

# 2. I/O 密集型任务演示（GIL 影响较小）
print(f"\n📝 2. I/O 密集型任务演示")
print("-" * 50)

def io_intensive_task(task_name, sleep_time=1):
    """I/O 密集型任务"""
    print(f"开始执行 {task_name} (线程ID: {threading.current_thread().ident})")
    start_time = time.time()
    
    # 模拟 I/O 等待
    time.sleep(sleep_time)
    
    end_time = time.time()
    print(f"{task_name} 完成，耗时: {end_time - start_time:.3f}秒")
    return end_time - start_time

def demonstrate_io_threading():
    """演示 I/O 密集型任务中多线程的优势"""
    sleep_time = 0.5
    
    print("🔄 单线程执行 I/O 任务:")
    start_time = time.time()
    io_intensive_task("I/O任务1", sleep_time)
    io_intensive_task("I/O任务2", sleep_time)
    single_thread_total = time.time() - start_time
    print(f"单线程总耗时: {single_thread_total:.3f}秒\n")
    
    print("🔄 多线程执行 I/O 任务:")
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future1 = executor.submit(io_intensive_task, "线程I/O任务1", sleep_time)
        future2 = executor.submit(io_intensive_task, "线程I/O任务2", sleep_time)
        
        future1.result()
        future2.result()
    
    multi_thread_total = time.time() - start_time
    print(f"多线程总耗时: {multi_thread_total:.3f}秒")
    print(f"加速比: {single_thread_total / multi_thread_total:.2f}x")
    
    if multi_thread_total < single_thread_total * 0.7:
        print("✅ 多线程在 I/O 密集型任务中有显著性能提升")

demonstrate_io_threading()

# 3. Mutex 演示：线程同步
print(f"\n📝 3. Mutex 演示：线程同步")
print("-" * 50)

def unsafe_increment(iterations):
    """不安全的计数器递增（没有锁保护）"""
    global counter
    thread_id = threading.current_thread().ident
    print(f"线程 {thread_id} 开始不安全递增")
    
    for i in range(iterations):
        # 这里存在竞态条件
        temp = counter
        temp += 1
        counter = temp
    
    print(f"线程 {thread_id} 完成不安全递增")

def safe_increment(iterations):
    """安全的计数器递增（使用锁保护）"""
    global counter, counter_lock
    thread_id = threading.current_thread().ident
    print(f"线程 {thread_id} 开始安全递增")
    
    for i in range(iterations):
        with counter_lock:  # 使用 mutex 保护临界区
            temp = counter
            temp += 1
            counter = temp
    
    print(f"线程 {thread_id} 完成安全递增")

def demonstrate_mutex():
    """演示 mutex 的作用"""
    global counter
    iterations = 10000
    
    # 不安全的多线程递增
    print("🔄 不使用锁的多线程递增:")
    counter = 0
    threads = []
    
    for i in range(3):
        thread = threading.Thread(target=unsafe_increment, args=(iterations,))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    expected = 3 * iterations
    print(f"期望结果: {expected}")
    print(f"实际结果: {counter}")
    print(f"数据竞争导致的损失: {expected - counter}")
    
    print(f"\n🔒 使用锁的多线程递增:")
    counter = 0
    threads = []
    
    for i in range(3):
        thread = threading.Thread(target=safe_increment, args=(iterations,))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    print(f"期望结果: {expected}")
    print(f"实际结果: {counter}")
    if counter == expected:
        print("✅ 使用锁成功避免了数据竞争")
    else:
        print("❌ 仍存在数据竞争问题")

demonstrate_mutex()

# 4. 可重入锁 (RLock) 演示
print(f"\n📝 4. 可重入锁 (RLock) 演示")
print("-" * 50)

class Counter:
    def __init__(self):
        self._value = 0
        self._lock = RLock()  # 可重入锁
    
    def increment(self):
        with self._lock:
            self._value += 1
            print(f"递增后值: {self._value} (线程: {threading.current_thread().ident})")
    
    def increment_twice(self):
        """需要重复获取同一个锁"""
        with self._lock:
            print(f"开始双重递增 (线程: {threading.current_thread().ident})")
            self.increment()  # 这里会再次获取同一个锁
            self.increment()
            print(f"双重递增完成")
    
    @property
    def value(self):
        with self._lock:
            return self._value

def demonstrate_reentrant_lock():
    """演示可重入锁"""
    print("🔄 可重入锁演示:")
    counter = Counter()
    
    def worker():
        counter.increment_twice()
    
    threads = []
    for i in range(2):
        thread = threading.Thread(target=worker)
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    print(f"最终计数器值: {counter.value}")
    print("✅ 可重入锁允许同一线程多次获取锁")

demonstrate_reentrant_lock()

# 5. 死锁演示和避免
print(f"\n📝 5. 死锁演示和避免")
print("-" * 50)

lock1 = Lock()
lock2 = Lock()

def task_a():
    """任务 A：先获取 lock1，再获取 lock2"""
    print("任务 A：尝试获取 lock1")
    with lock1:
        print("任务 A：获取 lock1 成功")
        time.sleep(0.1)  # 模拟一些工作
        
        print("任务 A：尝试获取 lock2")
        try:
            # 使用 timeout 避免永久阻塞
            if lock2.acquire(timeout=0.5):
                try:
                    print("任务 A：获取 lock2 成功")
                    time.sleep(0.1)
                finally:
                    lock2.release()
            else:
                print("任务 A：获取 lock2 超时，避免死锁")
        except:
            pass

def task_b():
    """任务 B：先获取 lock2，再获取 lock1"""
    print("任务 B：尝试获取 lock2")
    with lock2:
        print("任务 B：获取 lock2 成功")
        time.sleep(0.1)  # 模拟一些工作
        
        print("任务 B：尝试获取 lock1")
        try:
            # 使用 timeout 避免永久阻塞
            if lock1.acquire(timeout=0.5):
                try:
                    print("任务 B：获取 lock1 成功")
                    time.sleep(0.1)
                finally:
                    lock1.release()
            else:
                print("任务 B：获取 lock1 超时，避免死锁")
        except:
            pass

def demonstrate_deadlock_avoidance():
    """演示死锁避免"""
    print("🔄 死锁避免演示 (使用超时):")
    
    thread_a = threading.Thread(target=task_a)
    thread_b = threading.Thread(target=task_b)
    
    thread_a.start()
    thread_b.start()
    
    thread_a.join()
    thread_b.join()
    
    print("✅ 通过超时机制成功避免了死锁")

demonstrate_deadlock_avoidance()

# 6. 多进程演示（绕过 GIL）
print(f"\n📝 6. 多进程演示（绕过 GIL）")
print("-" * 50)

def cpu_task_for_multiprocessing(n):
    """用于多进程的 CPU 密集型任务"""
    result = 0
    for i in range(n):
        result += i ** 2
    return result

def demonstrate_multiprocessing():
    """演示多进程绕过 GIL 限制"""
    n = 500000
    
    print("🔄 多进程执行 CPU 密集型任务:")
    start_time = time.time()
    
    # 使用进程池
    with multiprocessing.Pool(processes=2) as pool:
        futures = [pool.apply_async(cpu_task_for_multiprocessing, (n,)) for _ in range(2)]
        results = [future.get() for future in futures]
    
    multiprocessing_time = time.time() - start_time
    print(f"多进程耗时: {multiprocessing_time:.3f}秒")
    print(f"结果: {results}")
    print("✅ 多进程可以真正并行执行 CPU 密集型任务，绕过 GIL 限制")

# 只在主进程中运行多进程演示
if __name__ == "__main__":
    demonstrate_multiprocessing()

# 7. 总结
print(f"\n📋 总结：GIL 和 Mutex 的关键概念")
print("=" * 80)

print("""
🔒 GIL (Global Interpreter Lock):
   • Python 的全局解释器锁，确保同时只有一个线程执行 Python 字节码
   • 限制了多线程在 CPU 密集型任务中的性能提升
   • 对 I/O 密集型任务影响较小，因为 I/O 操作会释放 GIL
   • 可以通过多进程绕过 GIL 限制

🔐 Mutex (互斥锁):
   • 用于保护共享资源，防止多个线程同时访问临界区
   • threading.Lock() 是最基本的互斥锁
   • threading.RLock() 是可重入锁，同一线程可以多次获取
   • 正确使用锁可以避免数据竞争和竞态条件

⚠️  注意事项:
   • 锁的获取顺序要一致，避免死锁
   • 使用 timeout 可以避免永久阻塞
   • 过多的锁会影响性能，需要平衡安全性和性能
   • 对于 CPU 密集型任务，考虑使用多进程而不是多线程

💡 最佳实践:
   • I/O 密集型任务使用多线程
   • CPU 密集型任务使用多进程
   • 使用 with 语句自动管理锁的获取和释放
   • 优先使用高级同步原语 (Queue, Event, Condition 等)
""")

print(f"\n🔚 GIL 和 Mutex 演示完成！")
