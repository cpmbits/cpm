from cpm.domain.project.project_description import ProjectDescription, TargetDescription, DeclaredBit, CompilationPlan, PackageDescription


def parse_compilation_plan(plan_description):
    compilation_plan = CompilationPlan()
    for bit_name in plan_description.get('bits', {}):
        declared_bit = DeclaredBit(bit_name, plan_description['bits'][bit_name])
        compilation_plan.declared_bits.append(declared_bit)
    for package_path in plan_description.get('packages', {}):
        package = PackageDescription(package_path,
                                     cflags=package_cflags(plan_description['packages'][package_path]))
        compilation_plan.packages.append(package)
    compilation_plan.cflags = plan_description.get('cflags', [])
    compilation_plan.cppflags = plan_description.get('cppflags', [])
    compilation_plan.libraries = plan_description.get('libraries', [])
    return compilation_plan


def parse_target(target_name, target_description):
    target = TargetDescription(target_name)
    target.image = target_description.get('image', '')
    target.build = parse_compilation_plan(target_description.get('build', {}))
    target.test = parse_compilation_plan(target_description.get('test', {}))
    return target


def parse_targets(targets_description):
    targets = {
        'default': TargetDescription('default')
    }
    for target_name in targets_description:
        targets[target_name] = parse_target(target_name, targets_description[target_name])
    return targets


def parse(project_description):
    project = ProjectDescription(project_description['name'])
    project.version = project_description.get('version', '')
    project.description = project_description.get('description', '')
    project.build = parse_compilation_plan(project_description.get('build', {}))
    project.test = parse_compilation_plan(project_description.get('test', {}))
    project.targets = parse_targets(project_description.get('targets', {}))
    return project


def package_cflags(package_description):
    return package_description.get('cflags', []) if type(package_description) is dict else []
