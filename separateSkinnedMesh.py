# author Oleksii Zinchenko 2024

import maya.cmds as cmds
import maya.mel as mel


def CombineSkinnedMeshProc(*args):
    name = cmds.textField('name_fld', q=True, tx=True)
    if name:
        sel = cmds.ls(sl=True)
        if sel:
            if len(sel) > 1:
                if not cmds.objExists('generated_geo'):
                    cmds.group(em=True, n='generated_geo')

                for i in range(len(sel)):
                    cmds.duplicate(sel[i], n='mesh_for_duplicate_%s' % str(i))
                t = cmds.ls('mesh_for_duplicate_*', r=True, s=False)
                cmds.polyUnite(t, n=name, op=True, muv=1)
                cmds.delete(name, ch=True)
                cmds.parent(name, 'generated_geo')
                # copy skin
                cmds.select(cl=True)
                inf = []
                for a in sel:
                    tmp = mel.eval('findRelatedSkinCluster %s' % a)
                    if tmp:
                        cmds.skinPercent(tmp, a, prw=0.01)
                        t = cmds.skinCluster(tmp, q=True, inf=True)
                        for j in t:
                            if not j in inf:
                                inf.append(j)
                cmds.skinCluster(inf, name, bm=True, lw=False, omi=True, tsb=True, mi=5, nw=1,
                                 n='%s_skinCluster' % name)
                for a in sel:
                    cmds.select(a, add=True)
                cmds.select(name, add=True)
                mel.eval('CopySkinWeights')
                cmds.select(cl=True)
                cmds.skinCluster('%s_skinCluster' % name, e=True, rui=True)
                # clear scene
                t = cmds.ls('mesh_for_duplicate_*', r=True, s=False)
                if t:
                    for a in t:
                        if cmds.objExists(a):
                            cmds.delete(a)

                print('// Result: %s skinned mesh combined.' % name)
            else:
                cmds.warning('Selected less then two objects!')
        else:
            cmds.warning('Nothing selected!')
    else:
        cmds.warning('No name!')


def SeparateSkinnedMeshProc():
    sel = cmds.ls(sl=True)
    if sel:
        name = cmds.textField('name_fld', q=True, tx=True)
        if name:
            obj = sel[0].split('.')[0]
            skin = mel.eval('findRelatedSkinCluster %s' % obj)
            if skin:
                if not cmds.objExists('generated_geo'):
                    cmds.group(em=True, n='generated_geo')

                cmds.duplicate(obj, n=name)
                cmds.select(cl=True)
                for a in sel:
                    cmds.select('%s.%s' % (name, a[len(obj) + 1:]), add=True)
                mel.eval('invertSelection')
                t = cmds.ls(sl=True)
                cmds.delete(t)
                cmds.delete(name, ch=True)
                cmds.parent(name, 'generated_geo')
                # copy skin
                cmds.skinPercent(skin, obj, prw=0.01)
                inf = cmds.skinCluster(skin, q=True, inf=True)
                cmds.skinCluster(inf, name, bm=True, lw=False, omi=True, tsb=True, mi=5, nw=1,
                                 n='%s_skinCluster' % name)
                cmds.copySkinWeights(ss=skin, ds='%s_skinCluster' % name, nm=True, sa='closestPoint', ia='closestJoint')
                cmds.skinCluster('%s_skinCluster' % name, e=True, rui=True)
                if cmds.checkBox('del_cbox', q=True, v=True):
                    cmds.delete(sel)
                    cmds.select(obj, r=True)
                    mel.eval('doBakeNonDefHistory( 1, {"prePost" })')
                print('// Result: %s skinned mesh separated.' % name)
            else:
                cmds.warning('Selected mesh without skinCluster!')
        else:
            cmds.warning('No name!')
    else:
        cmds.warning('Nothing selected!')


def separateMesh_UI():
    if cmds.window('CombSepSkinMeshWin', ex=True):
        cmds.deleteUI('CombSepSkinMeshWin')
    cmds.window("CombSepSkinMeshWin", t="Combine Separate Skinned Mesh", s=0)
    cmds.rowColumnLayout('case', nc=1, cal=(1, 'left'), rs=(1, 5), cs=(1, 5), cw=(1, 290), p='CombSepSkinMeshWin')
    cmds.text(l='', h=1, p='case')

    cmds.rowColumnLayout('opt_rc', nc=2, cal=[(1, 'right'), (2, 'center')], rs=[(1, 15), (2, 5)], cs=[(1, 5), (2, 5)],
                         cw=[(1, 220), (2, 20)], p='case')
    cmds.text(l='delete separated faces from origin mesh:', p='opt_rc')
    cmds.checkBox('del_cbox', l='', v=False, p='opt_rc')

    cmds.rowColumnLayout('name_rc', nc=2, cal=[(1, 'right'), (2, 'center')], rs=[(1, 5), (2, 5)], cs=[(1, 5), (2, 5)],
                         cw=[(1, 30), (2, 250)], p='case')
    cmds.text(l='name:', p='name_rc')
    cmds.textField('name_fld', tx='', p='name_rc')

    cmds.button(l='Combine Skinned Mesh', c=lambda x: CombineSkinnedMeshProc(), p='case')
    cmds.button(l='Separate Skinned Mesh', c=lambda x: SeparateSkinnedMeshProc(), p='case')
    cmds.showWindow("CombSepSkinMeshWin")
    cmds.window("CombSepSkinMeshWin", e=True, wh=(300, 110))
