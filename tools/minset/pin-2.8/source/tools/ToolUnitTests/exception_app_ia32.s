.text

## unsigned int RaiseIntDivideByZeroException(unsigned int (*)(), unsigned int);

.global RaiseIntDivideByZeroException

.type RaiseIntDivideByZeroException, @function
RaiseIntDivideByZeroException:
    push %ebp
    mov %esp, %ebp
    push %ebx # save ebx
    mov 0x8(%ebp), %ebx # fptr
    mov 0xc(%ebp), %esi # except code
    push %esi
    xor %eax, %eax
    idiv %eax
    leave
    ret
    
.global CatchIntDivideByZeroException

.type CatchIntDivideByZeroException, @function
CatchIntDivideByZeroException:
    pop %eax # exc code -> %eax
    pop %ebx
    leave
    ret
    
.global UnmaskFpZeroDivide
.type UnmaskFpZeroDivide, @function
UnmaskFpZeroDivide:
  push %ebp
  mov %esp, %ebp
  call GetFCW
  mov $0x4, %edi
  not %edi
  and %edi, %eax
  push %eax
  call SetFCW
  leave
  ret
  
.global MaskFpZeroDivide
.type MaskFpZeroDivide, @function
MaskFpZeroDivide:
  push %ebp
  mov %esp, %ebp
  call GetFCW
  mov $0x4, %edi
  or %edi, %eax
  push %eax
  call SetFCW
  fnclex
  leave
  ret

.global GetFCW
.type GetFCW, @function
GetFCW:
 xor %eax, %eax
 push %eax
 fstcw (%esp)
 pop %eax
 ret


.global SetFCW
.type SetFCW, @function
SetFCW:
   push %ebp
   mov %esp, %ebp
   fnclex
   fldcw 8(%ebp)
   fnclex
   leave
   ret
