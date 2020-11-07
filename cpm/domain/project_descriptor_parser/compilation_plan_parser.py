from cpm.domain.project.compilation_plan import CompilationPlan, DeclaredBit, Package


def parse(plan_description):
    compilation_plan = CompilationPlan()
    for bit_name in plan_description.get('bits', {}):
        declared_bit = DeclaredBit(bit_name, plan_description['bits'][bit_name])
        compilation_plan.bits.append(declared_bit)
    for package_path in plan_description.get('packages', {}):
        package = Package(package_path,
                          cflags=plan_description['packages'][package_path].get('cflags', []))
        compilation_plan.packages.append(package)
    compilation_plan.cflags = plan_description.get('cflags', [])
    compilation_plan.cppflags = plan_description.get('cppflags', [])
    compilation_plan.libraries = plan_description.get('libraries', [])
    return compilation_plan
