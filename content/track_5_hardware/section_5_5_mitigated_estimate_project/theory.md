## Where the missing 0.2 goes

A three-qubit GHZ state $(|000\rangle+|111\rangle)/\sqrt2$ has $\langle Z_0Z_2\rangle=1$: qubits 0 and 2 always agree. On the noisy device of this project, 20000 shots of the circuit give about 0.80. Two causes from lesson 5.3 share the gap, and you can estimate the first by hand. The device reads a true 0 as 0 with probability 0.98 and a true 1 as 1 with probability 0.94, so the measured $Z$ of one qubit is $0.98-0.02 = 0.96$ for a true 0 and $-(0.94-0.06) = -0.88$ for a true 1. On GHZ half the shots are $000$ and half are $111$, and $Z_0Z_2$ is the product for two qubits: $0.96^2 = 0.922$ and $0.88^2 = 0.774$, average $0.848$. Readout alone would cost 0.15, and the rest, about 0.06 once readout is corrected, comes from the depolarizing noise after each of the three gates.

Mitigating the readout is a matrix inverse. At scale 1 it brings the value to about 0.94, and what is left is entirely the gates. That part is attacked by folding, as in lesson 5.4: at scales 1, 3, 5 the readout-mitigated values are about 0.941, 0.833 and 0.737, and a line through them reaches 0.990 at scale 0. The project is to build this whole pipeline from the device's counts and then say how much to trust it.

## The pieces

The circuit is a Hadamard gate on qubit 0 followed by CNOT gates 0→1 and 1→2, which respect the line of three qubits. To fold it, write the gate list as $G$ and form $G\,(G^\dagger G)^k$ for scale $s=2k+1$; $H$, $X$ and CNOT are their own inverses, so $G^\dagger$ is the same list reversed.

For the assignment matrix, prepare each of the 8 basis states (`calibrate` does it), and fill column $j$ with the frequencies read for prepared state $j$. The rows are what was read and the columns what was prepared; swapping them is the most common slip, and gives the transpose. Solve $p_\text{meas}=A\,p_\text{true}$ at every scale before computing $\langle Z_0Z_2\rangle$, then fit the three values and read the fit at 0.

Count keys here write qubit 0 first, `'q0 q1 q2'`, so `'100'` means qubit 0 read 1. Qiskit writes the same outcome as `'001'` (the correlator $Z_0Z_2$ looks the same in both orders, but a matrix indexed one way and a distribution indexed the other is a bug).

## How much to trust it

One run is one sample. Run the whole estimate again with another seed and you get a slightly different number, and the standard deviation over several seeds is the statistical uncertainty of a single run. With 20000 shots one measurement fluctuates by about $1/\sqrt{20000}\approx0.007$. The estimate here comes out close to that value, a little larger, because the inversion of $A$ and the extrapolation amplify the noise while a correlator near 1 fluctuates less than one near 0. The point of reporting $\sigma$ is that a mitigated value without it cannot be compared with anything.
